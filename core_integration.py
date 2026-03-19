# core_integration.py: نظام موحد لربط جميع تطبيقات Python
"""
نظام التكامل المركزي - يربط جميع المكونات ببعضها
Central Integration System - Connects all components together
"""
import logging
import os
from typing import Optional, Dict, Any
from threading import Lock

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Singleton instances with thread safety
_instances = {}
_locks = {}
_initialized = False

class CoreIntegration:
    """نظام التكامل المركزي - يربط جميع المكونات"""
    
    def __init__(self):
        self.chatbot = None
        self.database = None
        self.web_scraper = None
        self.scraper_manager = None
        self.web_search_service = None  # جديد - للبحث في الإنترنت مباشرة
        self.analytics = None
        self.vector_db = None
        self.knowledge_base = None
        self.conversation_memory = None
        self.llm_manager = None
        self.initialized = False
        
    def initialize_all(self):
        """تهيئة جميع المكونات"""
        if self.initialized:
            logger.info("Core integration already initialized")
            return True
        
        logger.info("="*60)
        logger.info("🚀 Initializing Core Integration System")
        logger.info("="*60)
        
        try:
            # 1. Initialize Database
            logger.info("[1/8] Initializing Database...")
            try:
                from database import Base, engine, Session
                Base.metadata.create_all(engine)
                self.database = {
                    'engine': engine,
                    'Session': Session,
                    'Base': Base
                }
                logger.info("✅ Database initialized")
            except Exception as e:
                logger.error(f"❌ Database initialization failed: {e}")
                self.database = None
            
            # 2. Initialize Chatbot
            logger.info("[2/8] Initializing Chatbot...")
            try:
                from advanced_chatbot_integration import AdvancedChatbot
                self.chatbot = AdvancedChatbot()
                logger.info("✅ Chatbot initialized")
            except Exception as e:
                logger.error(f"❌ Chatbot initialization failed: {e}")
                # Create fallback
                self.chatbot = self._create_fallback_chatbot()
                logger.warning("⚠️ Using fallback chatbot")
            
            # 3. Initialize Web Scraper
            logger.info("[3/8] Initializing Web Scraper...")
            try:
                from web_scraper import get_web_scraper
                self.web_scraper = get_web_scraper()
                logger.info("✅ Web Scraper initialized")
            except Exception as e:
                logger.warning(f"⚠️ Web Scraper initialization failed: {e}")
                self.web_scraper = None
            
            # 4. Initialize Scraper Manager
            logger.info("[4/8] Initializing Scraper Manager...")
            try:
                from scraper_manager import get_scraper_manager
                self.scraper_manager = get_scraper_manager()
                logger.info("✅ Scraper Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️ Scraper Manager initialization failed: {e}")
                self.scraper_manager = None
            
            # 4.5. Initialize Web Search Service (جديد - للبحث في الإنترنت مباشرة)
            logger.info("[4.5/8] Initializing Web Search Service...")
            try:
                from web_search_service import get_web_search_service
                self.web_search_service = get_web_search_service()
                logger.info("✅ Web Search Service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Web Search Service initialization failed: {e}")
                self.web_search_service = None
            
            # 5. Initialize Analytics
            logger.info("[5/8] Initializing Analytics...")
            try:
                from analytics_dashboard import AnalyticsDashboard
                self.analytics = AnalyticsDashboard
                logger.info("✅ Analytics initialized")
            except Exception as e:
                logger.warning(f"⚠️ Analytics initialization failed: {e}")
                self.analytics = None
            
            # 6. Initialize Vector Database
            logger.info("[6/8] Initializing Vector Database...")
            try:
                from vector_database import get_vector_database
                self.vector_db = get_vector_database()
                logger.info("✅ Vector Database initialized")
            except Exception as e:
                logger.warning(f"⚠️ Vector Database initialization failed: {e}")
                self.vector_db = None
            
            # 7. Initialize Knowledge Base
            logger.info("[7/8] Initializing Knowledge Base...")
            try:
                from ai_knowledge_base import get_knowledge_base
                self.knowledge_base = get_knowledge_base()
                logger.info("✅ Knowledge Base initialized")
            except Exception as e:
                logger.warning(f"⚠️ Knowledge Base initialization failed: {e}")
                self.knowledge_base = None
            
            # 8. Initialize Conversation Memory
            logger.info("[8/8] Initializing Conversation Memory...")
            try:
                from conversation_memory import get_conversation_memory
                self.conversation_memory = get_conversation_memory()
                logger.info("✅ Conversation Memory initialized")
            except Exception as e:
                logger.warning(f"⚠️ Conversation Memory initialization failed: {e}")
                self.conversation_memory = None
            
            self.initialized = True
            logger.info("="*60)
            logger.info("✅ Core Integration System Initialized Successfully!")
            logger.info("="*60)
            self._print_status()
            return True
            
        except Exception as e:
            logger.error(f"❌ Critical error during initialization: {e}", exc_info=True)
            return False
    
    def _create_fallback_chatbot(self):
        """إنشاء شات بوت بديل ذكي - يبحث في الإنترنت"""
        class SmartFallbackChatbot:
            def __init__(self):
                self.web_search = None
                self.web_scraper = None
                try:
                    from web_search_service import get_web_search_service
                    self.web_search = get_web_search_service()
                except:
                    pass
                try:
                    from web_scraper import get_web_scraper
                    self.web_scraper = get_web_scraper()
                except:
                    pass
            
            def process_message(self, message, user_id='anonymous', lang=None, **kwargs):
                detected_lang = 'ar' if any('\u0600' <= char <= '\u06FF' for char in message) else 'en'
                
                # محاولة البحث في الإنترنت
                response = None
                try:
                    # 1. البحث في قاعدة البيانات الطبية أولاً (الأولوية!)
                    try:
                        from database import search_medical_data
                        medical_results = search_medical_data(message, limit=2)
                        if medical_results:
                            response = self._format_medical_results(medical_results, detected_lang)
                    except Exception as e:
                        logger.debug(f"Medical search error: {e}")
                    
                    # 2. إذا لم توجد بيانات طبية، ابحث في قاعدة البيانات المحلية
                    if not response:
                        try:
                            from database import search_scraped_data
                            results = search_scraped_data(message, limit=3)
                            if results:
                                response = self._format_results(results, detected_lang)
                        except:
                            pass
                    
                    # 2. إذا لم توجد نتائج، ابحث في الإنترنت
                    if not response and self.web_search:
                        web_results = self.web_search.search_and_scrape(message, max_results=2)
                        if web_results:
                            response = self._format_web_results(web_results, detected_lang)
                    
                    # 3. إذا لم توجد نتائج، ابحث بسيط في الإنترنت
                    if not response and self.web_search:
                        simple_results = self.web_search.search_web(message, max_results=2)
                        if simple_results:
                            response = self._format_simple_results(simple_results, detected_lang)
                    
                except Exception as e:
                    logger.debug(f"Fallback chatbot search error: {e}")
                
                # 4. إذا لم توجد نتائج، رد ذكي
                if not response:
                    if detected_lang == 'ar':
                        response = f"أهلاً! 🌟 أنا مساعد إيفا الذكي. سؤالك عن '{message}' مهم جداً! 💡\n\nأنا حالياً أبحث في الإنترنت للحصول على أحدث المعلومات... 🔍\n\n💬 يمكنك:\n• توضيح سؤالك أكثر\n• السؤال عن منتجات إيفا\n• الاستفسار عن العناية بالبشرة\n• أي سؤال آخر - أنا هنا لمساعدتك! 😊"
                    else:
                        response = f"Hello! 🌟 I'm Eva's smart assistant. Your question about '{message}' is very important! 💡\n\nI'm currently searching the web for the latest information... 🔍\n\n💬 You can:\n• Clarify your question more\n• Ask about Eva products\n• Inquire about skincare\n• Any other question - I'm here to help! 😊"
                
                return {
                    'response': response,
                    'detected_lang': detected_lang,
                    'intent': 'general',
                    'sentiment': 'neutral',
                    'confidence': 0.7,
                    'source': 'smart_fallback'
                }
            
            def _format_medical_results(self, results, lang):
                """تنسيق نتائج البحث الطبي"""
                if lang == 'ar':
                    response = "💊 معلومات طبية وصيدلانية:\n\n"
                else:
                    response = "💊 Medical and pharmacy information:\n\n"
                
                for i, result in enumerate(results[:2], 1):
                    title = result.get('title', '')
                    content = result.get('content', '')
                    dosage = result.get('dosage', '')
                    side_effects = result.get('side_effects', '')
                    contraindications = result.get('contraindications', '')
                    
                    response += f"**{title}**\n{content}\n"
                    if dosage:
                        response += f"💉 **الجرعة:** {dosage}\n"
                    if side_effects:
                        response += f"⚠️ **الآثار الجانبية:** {side_effects}\n"
                    if contraindications:
                        response += f"🚫 **موانع الاستخدام:** {contraindications}\n"
                    response += "\n"
                
                return response
            
            def _format_results(self, results, lang):
                """تنسيق نتائج البحث المحلية"""
                if lang == 'ar':
                    response = "📚 وجدت معلومات مفيدة:\n\n"
                else:
                    response = "📚 Found useful information:\n\n"
                
                for i, result in enumerate(results[:2], 1):
                    title = result.get('title', '')
                    content = result.get('content', '')[:300]
                    url = result.get('url', '')
                    
                    response += f"**{title}**\n{content}\n"
                    if url:
                        response += f"🔗 {url}\n"
                    response += "\n"
                
                return response
            
            def _format_web_results(self, results, lang):
                """تنسيق نتائج البحث من الإنترنت"""
                if lang == 'ar':
                    response = "🌐 معلومات من الإنترنت:\n\n"
                else:
                    response = "🌐 Information from the web:\n\n"
                
                for i, result in enumerate(results[:2], 1):
                    title = result.get('title', '')
                    content = result.get('content', '')[:300] or result.get('description', '')[:300]
                    url = result.get('url', '')
                    
                    response += f"**{title}**\n{content}\n"
                    if url:
                        response += f"🔗 {url}\n"
                    response += "\n"
                
                return response
            
            def _format_simple_results(self, results, lang):
                """تنسيق نتائج البحث البسيطة"""
                if lang == 'ar':
                    response = "🌐 معلومات من الإنترنت:\n\n"
                else:
                    response = "🌐 Information from the web:\n\n"
                
                for i, result in enumerate(results[:2], 1):
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    url = result.get('url', '')
                    
                    if title or snippet:
                        response += f"**{title}**\n{snippet}\n"
                        if url:
                            response += f"🔗 {url}\n"
                        response += "\n"
                
                return response
        
        return SmartFallbackChatbot()
    
    def _print_status(self):
        """طباعة حالة جميع المكونات"""
        logger.info("\n📊 System Status:")
        logger.info(f"  ✅ Chatbot: {'Loaded' if self.chatbot else 'Not Available'}")
        logger.info(f"  ✅ Database: {'Available' if self.database else 'Not Available'}")
        logger.info(f"  ✅ Web Scraper: {'Available' if self.web_scraper else 'Not Available'}")
        logger.info(f"  ✅ Scraper Manager: {'Available' if self.scraper_manager else 'Not Available'}")
        logger.info(f"  ✅ Analytics: {'Available' if self.analytics else 'Not Available'}")
        logger.info(f"  ✅ Vector DB: {'Available' if self.vector_db else 'Not Available'}")
        logger.info(f"  ✅ Knowledge Base: {'Available' if self.knowledge_base else 'Not Available'}")
        logger.info(f"  ✅ Conversation Memory: {'Available' if self.conversation_memory else 'Not Available'}")
        logger.info("")
    
    def get_chatbot(self):
        """الحصول على instance الشات بوت"""
        return self.chatbot
    
    def get_database(self):
        """الحصول على قاعدة البيانات"""
        return self.database
    
    def get_web_scraper(self):
        """الحصول على Web Scraper"""
        return self.web_scraper
    
    def get_scraper_manager(self):
        """الحصول على Scraper Manager"""
        return self.scraper_manager
    
    def get_web_search_service(self):
        """الحصول على Web Search Service"""
        return self.web_search_service
    
    def get_analytics(self):
        """الحصول على Analytics"""
        return self.analytics
    
    def get_vector_db(self):
        """الحصول على Vector Database"""
        return self.vector_db
    
    def get_knowledge_base(self):
        """الحصول على Knowledge Base"""
        return self.knowledge_base
    
    def get_conversation_memory(self):
        """الحصول على Conversation Memory"""
        return self.conversation_memory
    
    def is_ready(self):
        """التحقق من جاهزية النظام"""
        return self.initialized and self.chatbot is not None

# Singleton pattern with thread safety
_core_integration = None
_core_lock = Lock()

def get_core_integration() -> CoreIntegration:
    """الحصول على instance موحد من CoreIntegration"""
    global _core_integration
    
    with _core_lock:
        if _core_integration is None:
            _core_integration = CoreIntegration()
            _core_integration.initialize_all()
        elif not _core_integration.initialized:
            _core_integration.initialize_all()
    
    return _core_integration

# Convenience functions
def get_chatbot():
    """الحصول على الشات بوت"""
    return get_core_integration().get_chatbot()

def get_database():
    """الحصول على قاعدة البيانات"""
    return get_core_integration().get_database()

def get_web_scraper():
    """الحصول على Web Scraper"""
    return get_core_integration().get_web_scraper()

def get_scraper_manager():
    """الحصول على Scraper Manager"""
    return get_core_integration().get_scraper_manager()

def get_analytics():
    """الحصول على Analytics"""
    return get_core_integration().get_analytics()

def is_system_ready():
    """التحقق من جاهزية النظام"""
    return get_core_integration().is_ready()

# Initialize on import
if __name__ != '__main__':
    try:
        core = get_core_integration()
        logger.info("Core Integration System loaded")
    except Exception as e:
        logger.error(f"Failed to load Core Integration: {e}")

