# data_preprocessing.py: معالجة البيانات للتدريب
import pandas as pd
import numpy as np
from nlp_preprocessing import tokenize_text, remove_stopwords

def preprocess_data(data):
    df = pd.DataFrame(data)
    df['tokens'] = df['text'].apply(tokenize_text)
    df['tokens'] = df['tokens'].apply(remove_stopwords)
    return df

def load_data(file_path):
    return pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_json(file_path)