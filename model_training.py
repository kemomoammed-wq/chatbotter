# model_training.py: Model training logic with advanced training integration
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, filename='logs/chatbot.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import advanced training system
try:
    from advanced_training import AdvancedModelTrainer
    ADVANCED_TRAINING_AVAILABLE = True
except ImportError:
    ADVANCED_TRAINING_AVAILABLE = False
    logger.warning("Advanced training not available. Using legacy training.")

# Legacy imports for backward compatibility
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
import numpy as np
import joblib
import os

class ModelTrainer:
    def __init__(self):
        self.model_dir = 'models'
        os.makedirs(self.model_dir, exist_ok=True)

    def train_intent_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train a Random Forest model for intent recognition."""
        try:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            joblib.dump(model, os.path.join(self.model_dir, 'intent_model.pkl'))
            logger.info("Intent model trained and saved.")
            return {'model': 'intent_model', 'status': 'trained'}
        except Exception as e:
            logger.error(f"Error training intent model: {e}")
            raise

    def train_sentiment_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train an LSTM model for sentiment analysis."""
        try:
            model = Sequential([
                Embedding(input_dim=10000, output_dim=64),
                LSTM(64, return_sequences=True),
                LSTM(32),
                Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)
            model.save(os.path.join(self.model_dir, 'sentiment_model.h5'))
            logger.info("Sentiment model trained and saved.")
            return {'model': 'sentiment_model', 'status': 'trained'}
        except Exception as e:
            logger.error(f"Error training sentiment model: {e}")
            raise

def train_models(data: Dict, configs: Dict) -> Dict[str, Any]:
    """
    Train multiple models based on configuration.
    Uses advanced training system if available, falls back to legacy.
    """
    models = {}
    
    # Use advanced training system if available
    if ADVANCED_TRAINING_AVAILABLE:
        try:
            advanced_trainer = AdvancedModelTrainer()
            
            # Train intent model
            if configs.get('train_intent', False):
                algorithm = configs.get('intent_algorithm', 'ensemble')
                optimize = configs.get('optimize_hyperparameters', True)
                
                result = advanced_trainer.train_intent_classifier(
                    data['X_intent'],
                    data['y_intent'],
                    algorithm=algorithm,
                    optimize_hyperparameters=optimize,
                    cv_folds=configs.get('cv_folds', 5)
                )
                models['intent'] = result
            
            # Train sentiment model
            if configs.get('train_sentiment', False):
                architecture = configs.get('sentiment_architecture', 'bilstm')
                epochs = configs.get('epochs', 50)
                
                result = advanced_trainer.train_deep_sentiment_model(
                    data['X_sentiment'],
                    data['y_sentiment'],
                    architecture=architecture,
                    epochs=epochs,
                    optimize=configs.get('optimize_hyperparameters', True)
                )
                models['sentiment'] = result
            
            logger.info("Models trained using advanced training system")
            return models
            
        except Exception as e:
            logger.error(f"Advanced training failed: {e}. Falling back to legacy.")
    
    # Fallback to legacy training
    trainer = ModelTrainer()
    if configs.get('train_intent', False):
        models.update(trainer.train_intent_model(data['X_intent'], data['y_intent']))
    if configs.get('train_sentiment', False):
        models.update(trainer.train_sentiment_model(data['X_sentiment'], data['y_sentiment']))
    
    return models