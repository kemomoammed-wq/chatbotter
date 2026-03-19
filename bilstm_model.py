# bilstm_model.py: نماذج Bi-LSTM لتصنيف النية
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Bidirectional
import torch
import torch.nn as nn
import numpy as np

# نموذج TensorFlow Bi-LSTM
def build_tf_bilstm(vocab_size, embedding_dim=64, hidden_dim=128):
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=50),
        Bidirectional(LSTM(hidden_dim)),
        Dense(64, activation='relu'),
        Dense(3, activation='softmax')  # 3 فئات للنية
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# نموذج PyTorch Bi-LSTM
class PyTorchBiLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_dim=64, hidden_dim=128):
        super(PyTorchBiLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_dim * 2, 3)  # *2 لأن Bi-LSTM
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        embedded = self.embedding(x)
        output, _ = self.lstm(embedded)
        output = self.fc(output[:, -1, :])
        return self.softmax(output)

# تحويل النصوص إلى تسلسلات
def text_to_sequence(texts, vocab_size=1000):
    tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=vocab_size)
    tokenizer.fit_on_texts(texts)
    return tokenizer.texts_to_sequences(texts)