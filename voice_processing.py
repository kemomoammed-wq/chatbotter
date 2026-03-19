# voice_processing.py: معالجة الصوت والتعرف على الكلام وتحويل النص إلى كلام
import speech_recognition as sr
import pyttsx3
import pyaudio
import wave
import tempfile
import os
import logging
from typing import Optional, Dict, Any
import asyncio
import threading

logging.basicConfig(level=logging.INFO, filename='logs/chatbot.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self):
        """تهيئة معالج الصوت"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        self.is_listening = False
        self.setup_tts()
        
    def setup_tts(self):
        """إعداد محرك تحويل النص إلى كلام"""
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            
            # البحث عن صوت عربي إذا كان متوفراً
            for voice in voices:
                if 'arabic' in voice.name.lower() or 'ar' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # إعداد سرعة الكلام
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up TTS: {e}")
    
    def speech_to_text(self, audio_data: bytes = None, language: str = 'en') -> Dict[str, Any]:
        """تحويل الكلام إلى نص"""
        try:
            if audio_data:
                # معالجة البيانات الصوتية المرسلة
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_file.write(audio_data)
                    temp_file_path = temp_file.name
                
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                os.unlink(temp_file_path)
            else:
                # تسجيل مباشر من الميكروفون
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # التعرف على الكلام
            if language == 'ar':
                text = self.recognizer.recognize_google(audio, language='ar-SA')
            else:
                text = self.recognizer.recognize_google(audio, language='en-US')
            
            return {
                'success': True,
                'text': text,
                'confidence': 0.8,  # تقدير الثقة
                'language': language
            }
            
        except sr.WaitTimeoutError:
            return {
                'success': False,
                'error': 'No speech detected within timeout period',
                'text': '',
                'confidence': 0.0,
                'language': language
            }
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand the audio',
                'text': '',
                'confidence': 0.0,
                'language': language
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Speech recognition service error: {e}',
                'text': '',
                'confidence': 0.0,
                'language': language
            }
        except Exception as e:
            logger.error(f"Error in speech_to_text: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {e}',
                'text': '',
                'confidence': 0.0,
                'language': language
            }
    
    def text_to_speech(self, text: str, language: str = 'en') -> bool:
        """تحويل النص إلى كلام"""
        try:
            if not self.tts_engine:
                self.setup_tts()
            
            if language == 'ar':
                # إعداد صوت عربي إذا كان متوفراً
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'arabic' in voice.name.lower() or 'ar' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
            
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            return False
    
    def start_listening(self, callback, language: str = 'en'):
        """بدء الاستماع المستمر"""
        def listen_continuously():
            self.is_listening = True
            while self.is_listening:
                try:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source)
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    result = self.speech_to_text(audio_data=None, language=language)
                    if result['success'] and result['text'].strip():
                        callback(result)
                        
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in continuous listening: {e}")
                    break
        
        thread = threading.Thread(target=listen_continuously)
        thread.daemon = True
        thread.start()
        return thread
    
    def stop_listening(self):
        """إيقاف الاستماع"""
        self.is_listening = False
    
    def get_available_voices(self) -> list:
        """الحصول على الأصوات المتاحة"""
        try:
            if not self.tts_engine:
                self.setup_tts()
            
            voices = self.tts_engine.getProperty('voices')
            return [{'id': voice.id, 'name': voice.name, 'languages': voice.languages} for voice in voices]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """تحديد الصوت المستخدم"""
        try:
            if not self.tts_engine:
                self.setup_tts()
            
            self.tts_engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False

# دالة مساعدة للتعامل مع الملفات الصوتية
def process_audio_file(file_path: str, language: str = 'en') -> Dict[str, Any]:
    """معالجة ملف صوتي"""
    try:
        with sr.AudioFile(file_path) as source:
            recognizer = sr.Recognizer()
            audio = recognizer.record(source)
            
        if language == 'ar':
            text = recognizer.recognize_google(audio, language='ar-SA')
        else:
            text = recognizer.recognize_google(audio, language='en-US')
        
        return {
            'success': True,
            'text': text,
            'confidence': 0.8,
            'language': language
        }
    except Exception as e:
        logger.error(f"Error processing audio file: {e}")
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'confidence': 0.0,
            'language': language
        }

# دالة لتحسين جودة الصوت
def enhance_audio(audio_data: bytes) -> bytes:
    """تحسين جودة الصوت"""
    try:
        import numpy as np
        from scipy import signal
        
        # تحويل البيانات إلى مصفوفة numpy
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # تطبيق مرشح لإزالة الضوضاء
        b, a = signal.butter(5, 0.1, 'high')
        filtered_audio = signal.filtfilt(b, a, audio_array)
        
        # تطبيق ضغط ديناميكي
        compressed_audio = np.tanh(filtered_audio / 1000) * 1000
        
        return compressed_audio.astype(np.int16).tobytes()
    except Exception as e:
        logger.error(f"Error enhancing audio: {e}")
        return audio_data
