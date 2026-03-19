# advanced_training.py: Advanced Training System with Fine-tuning, Hyperparameter Optimization, and Model Management
import logging
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import optuna
from optuna import Trial

# Deep Learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Embedding, Dropout, BatchNormalization, Attention, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Transformers
try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorWithPadding,
        pipeline
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Some features will be disabled.")

# PyTorch
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Some features will be disabled.")

logger = logging.getLogger(__name__)

class AdvancedModelTrainer:
    """Advanced training system with multiple algorithms, fine-tuning, and optimization"""
    
    def __init__(self, model_dir: str = 'models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.training_history = []
        self.best_models = {}
        
    def train_intent_classifier(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        algorithm: str = 'ensemble',
        optimize_hyperparameters: bool = True,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train intent classifier with multiple algorithms and optimization
        
        Algorithms: 'random_forest', 'gradient_boosting', 'svm', 'logistic', 'ensemble'
        """
        try:
            start_time = time.time()
            
            # Split validation if not provided
            if X_val is None or y_val is None:
                X_train, X_val, y_train, y_val = train_test_split(
                    X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
                )
            
            if algorithm == 'ensemble':
                model = self._train_ensemble_intent(X_train, y_train, X_val, y_val, optimize_hyperparameters)
            elif algorithm == 'random_forest':
                model = self._train_random_forest(X_train, y_train, X_val, y_val, optimize_hyperparameters, cv_folds)
            elif algorithm == 'gradient_boosting':
                model = self._train_gradient_boosting(X_train, y_train, X_val, y_val, optimize_hyperparameters, cv_folds)
            elif algorithm == 'svm':
                model = self._train_svm(X_train, y_train, X_val, y_val, optimize_hyperparameters, cv_folds)
            elif algorithm == 'logistic':
                model = self._train_logistic(X_train, y_train, X_val, y_val, optimize_hyperparameters, cv_folds)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            val_score = model.score(X_val, y_val)
            
            y_pred = model.predict(X_val)
            precision = precision_score(y_val, y_pred, average='weighted')
            recall = recall_score(y_val, y_pred, average='weighted')
            f1 = f1_score(y_val, y_pred, average='weighted')
            
            # Save model
            model_path = self.model_dir / f'intent_model_{algorithm}_{int(time.time())}.pkl'
            joblib.dump(model, model_path)
            
            # Save metadata
            metadata = {
                'algorithm': algorithm,
                'train_accuracy': float(train_score),
                'val_accuracy': float(val_score),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'training_time': time.time() - start_time,
                'model_path': str(model_path),
                'timestamp': datetime.now().isoformat(),
                'n_samples': len(X_train),
                'n_features': X_train.shape[1] if len(X_train.shape) > 1 else 1
            }
            
            metadata_path = model_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Intent model trained: {algorithm}, Accuracy: {val_score:.4f}")
            
            return {
                'status': 'success',
                'model': str(model_path),
                'metrics': metadata,
                'model_object': model
            }
            
        except Exception as e:
            logger.error(f"Error training intent classifier: {e}")
            raise
    
    def _train_ensemble_intent(
        self, X_train, y_train, X_val, y_val, optimize: bool
    ) -> VotingClassifier:
        """Train ensemble of multiple classifiers"""
        if optimize:
            # Optimize each component
            rf_params = self._optimize_random_forest_hyperparameters(X_train, y_train)
            gb_params = self._optimize_gradient_boosting_hyperparameters(X_train, y_train)
        else:
            rf_params = {}
            gb_params = {}
        
        estimators = [
            ('rf', RandomForestClassifier(n_estimators=100, random_state=42, **rf_params)),
            ('gb', GradientBoostingClassifier(random_state=42, **gb_params)),
            ('lr', LogisticRegression(random_state=42, max_iter=1000))
        ]
        
        ensemble = VotingClassifier(estimators=estimators, voting='soft')
        ensemble.fit(X_train, y_train)
        
        return ensemble
    
    def _train_random_forest(self, X_train, y_train, X_val, y_val, optimize: bool, cv_folds: int):
        """Train Random Forest with optimization"""
        if optimize:
            params = self._optimize_random_forest_hyperparameters(X_train, y_train)
        else:
            params = {'n_estimators': 100, 'max_depth': 10}
        
        model = RandomForestClassifier(random_state=42, **params)
        model.fit(X_train, y_train)
        
        return model
    
    def _train_gradient_boosting(self, X_train, y_train, X_val, y_val, optimize: bool, cv_folds: int):
        """Train Gradient Boosting with optimization"""
        if optimize:
            params = self._optimize_gradient_boosting_hyperparameters(X_train, y_train)
        else:
            params = {'n_estimators': 100, 'learning_rate': 0.1}
        
        model = GradientBoostingClassifier(random_state=42, **params)
        model.fit(X_train, y_train)
        
        return model
    
    def _train_svm(self, X_train, y_train, X_val, y_val, optimize: bool, cv_folds: int):
        """Train SVM with optimization"""
        if optimize:
            params = self._optimize_svm_hyperparameters(X_train, y_train)
        else:
            params = {'C': 1.0, 'kernel': 'rbf'}
        
        model = SVC(random_state=42, probability=True, **params)
        model.fit(X_train, y_train)
        
        return model
    
    def _train_logistic(self, X_train, y_train, X_val, y_val, optimize: bool, cv_folds: int):
        """Train Logistic Regression with optimization"""
        if optimize:
            params = self._optimize_logistic_hyperparameters(X_train, y_train)
        else:
            params = {'C': 1.0, 'max_iter': 1000}
        
        model = LogisticRegression(random_state=42, **params)
        model.fit(X_train, y_train)
        
        return model
    
    def _optimize_random_forest_hyperparameters(self, X, y, n_trials: int = 20) -> Dict:
        """Optimize Random Forest hyperparameters using Optuna"""
        def objective(trial: Trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 5, 30),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5)
            }
            model = RandomForestClassifier(random_state=42, **params)
            scores = cross_val_score(model, X, y, cv=3, n_jobs=-1)
            return scores.mean()
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        return study.best_params
    
    def _optimize_gradient_boosting_hyperparameters(self, X, y, n_trials: int = 20) -> Dict:
        """Optimize Gradient Boosting hyperparameters"""
        def objective(trial: Trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0)
            }
            model = GradientBoostingClassifier(random_state=42, **params)
            scores = cross_val_score(model, X, y, cv=3, n_jobs=-1)
            return scores.mean()
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        return study.best_params
    
    def _optimize_svm_hyperparameters(self, X, y, n_trials: int = 20) -> Dict:
        """Optimize SVM hyperparameters"""
        def objective(trial: Trial):
            params = {
                'C': trial.suggest_float('C', 0.1, 10.0, log=True),
                'kernel': trial.suggest_categorical('kernel', ['rbf', 'poly', 'linear']),
                'gamma': trial.suggest_categorical('gamma', ['scale', 'auto'])
            }
            model = SVC(random_state=42, probability=True, **params)
            scores = cross_val_score(model, X, y, cv=3, n_jobs=-1)
            return scores.mean()
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        return study.best_params
    
    def _optimize_logistic_hyperparameters(self, X, y, n_trials: int = 20) -> Dict:
        """Optimize Logistic Regression hyperparameters"""
        def objective(trial: Trial):
            params = {
                'C': trial.suggest_float('C', 0.01, 10.0, log=True),
                'solver': trial.suggest_categorical('solver', ['lbfgs', 'liblinear', 'saga'])
            }
            model = LogisticRegression(random_state=42, max_iter=1000, **params)
            scores = cross_val_score(model, X, y, cv=3, n_jobs=-1)
            return scores.mean()
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        return study.best_params
    
    def train_deep_sentiment_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        architecture: str = 'bilstm',
        max_length: int = 100,
        vocab_size: int = 10000,
        embedding_dim: int = 128,
        epochs: int = 50,
        batch_size: int = 32,
        optimize: bool = True
    ) -> Dict[str, Any]:
        """Train deep learning sentiment model with multiple architectures"""
        try:
            start_time = time.time()
            
            # Prepare data
            X_train = pad_sequences(X_train, maxlen=max_length)
            if X_val is not None:
                X_val = pad_sequences(X_val, maxlen=max_length)
            else:
                X_train, X_val, y_train, y_val = train_test_split(
                    X_train, y_train, test_size=0.2, random_state=42
                )
            
            # Build model
            if architecture == 'bilstm':
                model = self._build_bilstm_sentiment_model(vocab_size, embedding_dim, max_length)
            elif architecture == 'lstm':
                model = self._build_lstm_sentiment_model(vocab_size, embedding_dim, max_length)
            elif architecture == 'cnn_lstm':
                model = self._build_cnn_lstm_sentiment_model(vocab_size, embedding_dim, max_length)
            else:
                raise ValueError(f"Unknown architecture: {architecture}")
            
            # Callbacks
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6),
                ModelCheckpoint(
                    str(self.model_dir / f'sentiment_model_{architecture}_{int(time.time())}.h5'),
                    monitor='val_loss',
                    save_best_only=True
                ),
                TensorBoard(log_dir=str(self.model_dir / 'logs'))
            ]
            
            # Train
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            # Evaluate
            train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
            val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
            
            # Save
            model_path = self.model_dir / f'sentiment_model_{architecture}_{int(time.time())}.h5'
            model.save(str(model_path))
            
            metadata = {
                'architecture': architecture,
                'train_accuracy': float(train_acc),
                'val_accuracy': float(val_acc),
                'train_loss': float(train_loss),
                'val_loss': float(val_loss),
                'training_time': time.time() - start_time,
                'model_path': str(model_path),
                'timestamp': datetime.now().isoformat(),
                'epochs': len(history.history['loss']),
                'vocab_size': vocab_size,
                'embedding_dim': embedding_dim
            }
            
            metadata_path = model_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Sentiment model trained: {architecture}, Accuracy: {val_acc:.4f}")
            
            return {
                'status': 'success',
                'model': str(model_path),
                'metrics': metadata,
                'history': history.history,
                'model_object': model
            }
            
        except Exception as e:
            logger.error(f"Error training sentiment model: {e}")
            raise
    
    def _build_bilstm_sentiment_model(self, vocab_size: int, embedding_dim: int, max_length: int) -> Model:
        """Build BiLSTM sentiment model"""
        model = Sequential([
            Embedding(vocab_size, embedding_dim, input_length=max_length),
            Bidirectional(LSTM(64, return_sequences=True, dropout=0.2)),
            Bidirectional(LSTM(32, dropout=0.2)),
            Dense(64, activation='relu'),
            Dropout(0.3),
            BatchNormalization(),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_lstm_sentiment_model(self, vocab_size: int, embedding_dim: int, max_length: int) -> Model:
        """Build LSTM sentiment model"""
        model = Sequential([
            Embedding(vocab_size, embedding_dim, input_length=max_length),
            LSTM(128, return_sequences=True, dropout=0.2),
            LSTM(64, dropout=0.2),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_cnn_lstm_sentiment_model(self, vocab_size: int, embedding_dim: int, max_length: int) -> Model:
        """Build CNN-LSTM hybrid model"""
        from tensorflow.keras.layers import Conv1D, MaxPooling1D, GlobalMaxPooling1D
        
        model = Sequential([
            Embedding(vocab_size, embedding_dim, input_length=max_length),
            Conv1D(64, 3, activation='relu'),
            MaxPooling1D(2),
            LSTM(64, dropout=0.2),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def fine_tune_transformer(
        self,
        model_name: str,
        train_dataset: Dataset,
        val_dataset: Optional[Dataset] = None,
        output_dir: str = 'models/finetuned',
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ) -> Dict[str, Any]:
        """Fine-tune transformer model for downstream task"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library not available")
        
        try:
            start_time = time.time()
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Tokenize datasets
            def tokenize_function(examples):
                return tokenizer(examples['text'], truncation=True, padding=True, max_length=512)
            
            train_dataset = train_dataset.map(tokenize_function, batched=True)
            if val_dataset:
                val_dataset = val_dataset.map(tokenize_function, batched=True)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                learning_rate=learning_rate,
                warmup_steps=500,
                logging_dir=f'{output_dir}/logs',
                logging_steps=100,
                evaluation_strategy='epoch' if val_dataset else 'no',
                save_strategy='epoch',
                load_best_model_at_end=True if val_dataset else False,
            )
            
            # Data collator
            data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
            
            # Trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                data_collator=data_collator,
            )
            
            # Train
            train_result = trainer.train()
            
            # Evaluate
            if val_dataset:
                eval_result = trainer.evaluate()
            else:
                eval_result = {}
            
            # Save
            trainer.save_model()
            tokenizer.save_pretrained(output_dir)
            
            metadata = {
                'model_name': model_name,
                'train_loss': float(train_result.training_loss),
                'eval_loss': float(eval_result.get('eval_loss', 0)),
                'training_time': time.time() - start_time,
                'output_dir': output_dir,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Transformer fine-tuned: {model_name}")
            
            return {
                'status': 'success',
                'model_dir': output_dir,
                'metrics': metadata
            }
            
        except Exception as e:
            logger.error(f"Error fine-tuning transformer: {e}")
            raise
    
    def compare_models(self, X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
        """Compare multiple trained models on test set"""
        results = []
        
        # Load all models
        for model_file in self.model_dir.glob('*.pkl'):
            try:
                model = joblib.load(model_file)
                y_pred = model.predict(X_test)
                
                results.append({
                    'model': model_file.stem,
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, average='weighted'),
                    'recall': recall_score(y_test, y_pred, average='weighted'),
                    'f1_score': f1_score(y_test, y_pred, average='weighted')
                })
            except Exception as e:
                logger.warning(f"Could not load model {model_file}: {e}")
        
        return pd.DataFrame(results)

