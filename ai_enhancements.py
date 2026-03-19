# ai_enhancements.py: تحسينات الذكاء الاصطناعي المتقدمة
import openai
import requests
import json
import logging
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO, filename='logs/chatbot.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEnhancements:
    def __init__(self):
        """تهيئة تحسينات الذكاء الاصطناعي"""
        self.openai_api_key = "your-openai-api-key"  # يجب استبدالها بمفتاح حقيقي
        self.context_memory = {}
        self.conversation_history = {}
        self.user_preferences = {}
        self.knowledge_base = {}
        
    def set_openai_key(self, api_key: str):
        """تعيين مفتاح OpenAI API"""
        self.openai_api_key = api_key
        openai.api_key = api_key
    
    def generate_advanced_response(self, message: str, user_id: str, context: Dict = None) -> Dict[str, Any]:
        """توليد رد متقدم باستخدام الذكاء الاصطناعي"""
        try:
            # إعداد السياق
            if context is None:
                context = {}
            
            # الحصول على تاريخ المحادثة
            conversation_history = self.conversation_history.get(user_id, [])
            
            # بناء prompt متقدم
            system_prompt = self._build_system_prompt(user_id, context)
            user_prompt = self._build_user_prompt(message, conversation_history)
            
            # استخدام OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # حفظ المحادثة
            self._save_conversation(user_id, message, ai_response)
            
            # تحليل المشاعر المتقدم
            sentiment_analysis = self._analyze_sentiment_advanced(message)
            
            # استخراج الكلمات المفتاحية
            keywords = self._extract_keywords_advanced(message)
            
            # تحديد النية
            intent = self._classify_intent_advanced(message)
            
            return {
                'response': ai_response,
                'sentiment': sentiment_analysis,
                'keywords': keywords,
                'intent': intent,
                'confidence': 0.9,
                'context_used': len(conversation_history),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in generate_advanced_response: {e}")
            return {
                'response': 'عذراً، حدث خطأ في معالجة رسالتك. يرجى المحاولة مرة أخرى.',
                'sentiment': {'label': 'neutral', 'score': 0.0},
                'keywords': [],
                'intent': 'general',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _build_system_prompt(self, user_id: str, context: Dict) -> str:
        """بناء prompt النظام"""
        user_prefs = self.user_preferences.get(user_id, {})
        language = user_prefs.get('language', 'ar')
        
        if language == 'ar':
            return f"""أنت مساعد ذكي متقدم يتحدث العربية بطلاقة. 
            أنت مفيد ومهذب ومتعاون. 
            تجيب على الأسئلة بوضوح ودقة.
            تستخدم أمثلة مناسبة وتقدم نصائح مفيدة.
            السياق الحالي: {context}
            تفضيلات المستخدم: {user_prefs}"""
        else:
            return f"""You are an advanced AI assistant that speaks English fluently.
            You are helpful, polite, and cooperative.
            You answer questions clearly and accurately.
            You use appropriate examples and provide useful advice.
            Current context: {context}
            User preferences: {user_prefs}"""
    
    def _build_user_prompt(self, message: str, conversation_history: List) -> str:
        """بناء prompt المستخدم"""
        history_text = ""
        if conversation_history:
            history_text = "Previous conversation:\n" + "\n".join(conversation_history[-5:])
        
        return f"{history_text}\n\nCurrent message: {message}"
    
    def _save_conversation(self, user_id: str, message: str, response: str):
        """حفظ المحادثة"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append(f"User: {message}")
        self.conversation_history[user_id].append(f"Assistant: {response}")
        
        # الاحتفاظ بآخر 20 تبادل فقط
        if len(self.conversation_history[user_id]) > 40:
            self.conversation_history[user_id] = self.conversation_history[user_id][-40:]
    
    def _analyze_sentiment_advanced(self, text: str) -> Dict[str, Any]:
        """تحليل المشاعر المتقدم"""
        try:
            # استخدام OpenAI لتحليل المشاعر
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the given text. Return only a JSON object with 'label' (positive/negative/neutral) and 'score' (0-1)."},
                    {"role": "user", "content": text}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {'label': 'neutral', 'score': 0.5}
    
    def _extract_keywords_advanced(self, text: str) -> List[str]:
        """استخراج الكلمات المفتاحية المتقدم"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the most important keywords from the given text. Return only a JSON array of strings."},
                    {"role": "user", "content": text}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            keywords = json.loads(response.choices[0].message.content)
            return keywords if isinstance(keywords, list) else []
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def _classify_intent_advanced(self, text: str) -> str:
        """تصنيف النية المتقدم"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Classify the intent of the given text. Choose from: question, request, greeting, complaint, compliment, other. Return only the intent word."},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().lower()
            return intent if intent in ['question', 'request', 'greeting', 'complaint', 'compliment', 'other'] else 'other'
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return 'other'
    
    def generate_code(self, description: str, language: str = 'python') -> Dict[str, Any]:
        """توليد كود برمجي"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Generate {language} code based on the description. Include comments and explanations."},
                    {"role": "user", "content": description}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            code = response.choices[0].message.content
            return {
                'success': True,
                'code': code,
                'language': language,
                'description': description
            }
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': '',
                'language': language
            }
    
    def translate_text_advanced(self, text: str, target_language: str) -> Dict[str, Any]:
        """ترجمة متقدمة للنص"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Translate the following text to {target_language}. Maintain the original meaning and tone."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            translated_text = response.choices[0].message.content
            return {
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'target_language': target_language
            }
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_text': text,
                'translated_text': text
            }
    
    def summarize_text(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        """تلخيص النص"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Summarize the following text in no more than {max_length} characters. Keep the main points."},
                    {"role": "user", "content": text}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            return {
                'success': True,
                'original_text': text,
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary)
            }
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_text': text,
                'summary': text
            }
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """تعيين تفضيلات المستخدم"""
        self.user_preferences[user_id] = preferences
        logger.info(f"User preferences updated for {user_id}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """الحصول على تفضيلات المستخدم"""
        return self.user_preferences.get(user_id, {})
    
    def clear_conversation_history(self, user_id: str):
        """مسح تاريخ المحادثة"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
        logger.info(f"Conversation history cleared for {user_id}")
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """الحصول على ملخص المحادثة"""
        history = self.conversation_history.get(user_id, [])
        if not history:
            return {'message_count': 0, 'summary': 'No conversation history'}
        
        # حساب الإحصائيات
        user_messages = [msg for msg in history if msg.startswith('User:')]
        assistant_messages = [msg for msg in history if msg.startswith('Assistant:')]
        
        return {
            'message_count': len(history),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'last_message': history[-1] if history else None,
            'conversation_length': len(' '.join(history))
        }
