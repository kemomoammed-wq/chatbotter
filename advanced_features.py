# advanced_features.py: ميزات الـ AI المتقدمة
from duckduckgo_search import DDGS
from sklearn.ensemble import RandomForestClassifier
from sentence_transformers import SentenceTransformer
import asyncio

# البحث عبر الإنترنت
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
        return results
    except Exception as e:
        print(f"Error in search_web: {e}")
        return []

# تصنيف النية
class IntentClassifier:
    def __init__(self):
        try:
            self.model = RandomForestClassifier()
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.initialized = True
        except Exception as e:
            print(f"IntentClassifier initialization failed: {e}")
            self.model = None
            self.encoder = None
            self.initialized = False

    def train(self, X, y):
        if not self.initialized:
            return
        try:
            X_encoded = self.encoder.encode(X)
            self.model.fit(X_encoded, y)
        except Exception as e:
            print(f"Training failed: {e}")

    def predict(self, text):
        if not self.initialized:
            return 'general'
        try:
            encoded = self.encoder.encode([text])
            return self.model.predict(encoded)[0]
        except:
            return 'general'
    
    def predict_intent(self, text):
        """Predict intent with confidence"""
        if not self.initialized:
            # Simple keyword-based intent detection
            text_lower = text.lower()
            if any(word in text_lower for word in ['منتج', 'product', 'شراء', 'buy']):
                return {'intent': 'product_inquiry', 'confidence': 0.7}
            elif any(word in text_lower for word in ['مشكلة', 'problem', 'علاج', 'treatment']):
                return {'intent': 'problem_solving', 'confidence': 0.7}
            elif any(word in text_lower for word in ['روتين', 'routine', 'استخدام', 'use']):
                return {'intent': 'routine_advice', 'confidence': 0.7}
            else:
                return {'intent': 'general', 'confidence': 0.6}
        
        try:
            intent = self.predict(text)
            return {'intent': intent, 'confidence': 0.8}
        except:
            return {'intent': 'general', 'confidence': 0.6}