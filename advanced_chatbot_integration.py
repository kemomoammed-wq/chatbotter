# advanced_chatbot_integration.py: Advanced ChatGPT-like chatbot with LLM integration
import asyncio
import logging
import time
import base64
from io import BytesIO
from PIL import Image 
from joblib import Memory
from flask_caching import Cache
import requests

# Transformers - optional (don't fail if not available)
TRANSFORMERS_AVAILABLE = False
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, MarianTokenizer, MarianMTModel
    TRANSFORMERS_AVAILABLE = True
except (ImportError, ModuleNotFoundError, RuntimeError) as e:
    # Setup basic logging for fallback message
    import logging
    logging.basicConfig(level=logging.WARNING)
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"Transformers not available: {e}. Using fallback mode.")
    # Create dummy classes for fallback
    class DummyPipeline:
        def __call__(self, *args, **kwargs):
            return [{'generated_text': ''}]
    class DummyTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return DummyTokenizer()
        def __call__(self, *args, **kwargs):
            return {}
    class DummyModel:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return DummyModel()
        def generate(self, *args, **kwargs):
            return []
    pipeline = DummyPipeline
    AutoTokenizer = DummyTokenizer
    AutoModelForSeq2SeqLM = DummyModel
    MarianTokenizer = DummyTokenizer
    MarianMTModel = DummyModel

# Celery worker - optional (don't fail if not available)
CELERY_AVAILABLE = False
try:
    from celery_worker import process_ai_message
    CELERY_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    def process_ai_message(*args, **kwargs):
        return None
from nlp_preprocessing import preprocess_pipeline
from ai_knowledge_base import get_knowledge_base, AIKnowledgeBase
from llm_integration import get_llm_manager
from conversation_memory import get_conversation_memory
from vector_database import get_vector_database
from advanced_caching import get_advanced_cache
from web_scraper import get_web_scraper
from typing import Dict, Optional, Any, Iterator

# Setup logging
logging.basicConfig(level=logging.INFO, filename='logs/chatbot.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup caching
memory = Memory('cache', verbose=0)
cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

# Configuration
HUGGINGFACE_API_KEY = "your-huggingface-api-key-here"  # Replace with your key
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large"

# Load Hugging Face models
@memory.cache
def load_hf_model() -> Optional[pipeline]:
    """Load the BART model for text generation."""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available. Skipping HF model loading.")
        return None
    try:
        tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large")
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large")
        return pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)
    except Exception as e:
        logger.error(f"Failed to load HF model: {e}")
        return None

@memory.cache
def load_translation_model(source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
    """Load translation model for the specified language pair."""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available. Skipping translation model loading.")
        return None
    try:
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        return {'tokenizer': tokenizer, 'model': model}
    except Exception as e:
        logger.error(f"Failed to load translation model: {e}")
        return None

# Query Hugging Face API
async def query_huggingface_api(prompt: str) -> Optional[str]:
    """Query Hugging Face API for text generation."""
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json={"inputs": prompt}, timeout=10)
        response.raise_for_status()
        return response.json()[0]['generated_text']
    except Exception as e:
        logger.error(f"Error querying Hugging Face API: {e}")
        return None

# Apply artistic style to images
@memory.cache
def apply_artistic_style(image_data: str, style: str = "digital_art") -> str:
    """Apply a digital art style to the input image."""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available. Cannot apply artistic style.")
        return image_data
    try:
        from transformers import pipeline
        style_transfer = pipeline("image-to-image", model="nitrosocke/digital-art-style-transfer")
        image = Image.open(BytesIO(base64.b64decode(image_data.split(',')[1])))
        styled_image = style_transfer(image, style=style)
        buffered = BytesIO()
        styled_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logger.error(f"Error applying artistic style: {e}")
        return image_data

# Translate text
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text between languages."""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available. Returning original text.")
        return text
    try:
        translator = load_translation_model(source_lang, target_lang)
        if translator is None:
            return text
        inputs = translator['tokenizer'](text, return_tensors="pt", padding=True)
        translated = translator['model'].generate(**inputs)
        return translator['tokenizer'].decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        logger.error(f"Error in translate_text: {e}")
        return text

class AdvancedChatbot:
    """Advanced ChatGPT-like chatbot with LLM integration and conversation memory"""
    
    def __init__(self):
        # Initialize Web Search Service FIRST (essential for smart responses)
        try:
            from web_search_service import get_web_search_service
            self.web_search_service = get_web_search_service()
            logger.info("Web Search Service initialized successfully")
        except Exception as e:
            logger.warning(f"Web Search Service not available: {e}")
            self.web_search_service = None
        
        # Initialize Intent Classifier (optional - لا يفشل إذا لم يكن متاحاً)
        try:
            from advanced_features import IntentClassifier
            self.intent_recognizer = IntentClassifier()
        except Exception as e:
            logger.warning(f"IntentClassifier not available: {e}")
            self.intent_recognizer = None
        
        # Initialize LLM Manager (OpenAI, HuggingFace, Ollama)
        try:
            self.llm_manager = get_llm_manager()
            logger.info("LLM Manager initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize LLM Manager: {e}")
            self.llm_manager = None
        
        # Initialize Conversation Memory (ChatGPT-like)
        try:
            self.memory = get_conversation_memory()
            logger.info("Conversation Memory initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Conversation Memory: {e}")
            self.memory = None
        
        # Initialize Vector Database for RAG
        try:
            self.vector_db = get_vector_database()
            logger.info("Vector Database initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Vector Database: {e}")
            self.vector_db = None
        
        # Initialize Advanced Cache
        try:
            self.advanced_cache = get_advanced_cache()
            logger.info("Advanced Cache initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Advanced Cache: {e}")
            self.advanced_cache = None
        
        # Legacy support
        self.context = {}  # Simple context storage (deprecated)
        self.sentiment_analyzer = None  # Will be initialized when needed
        
        try:
            self.hf_pipeline = load_hf_model()
        except Exception as e:
            logger.warning(f"Could not load HF model: {e}. Will use LLM Manager.")
            self.hf_pipeline = None
        
        # تحميل قاعدة المعرفة الشاملة (RAG support)
        try:
            self.knowledge_base = get_knowledge_base()
            logger.info("Knowledge base loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            self.knowledge_base = None
        
        # System prompts (ChatGPT-like personality) - متخصص في الطب والصيدلة
        self.system_prompts = {
            'default': """أنت صيدلي وطبيب متخصص. مهمتك مساعدة المستخدمين في:
            - معلومات الأدوية والجرعات
            - العلاجات الطبية
            - الأعراض والأمراض
            - العناية بالصحة
            - منتجات الصيدلية
            
            أنت متخصص فقط في الطب والصيدلة. إذا سُئلت عن شيء خارج اختصاصك، توجه المستخدم لاستشارة طبيب.
            تكون دقيقاً ومهذباً في ردودك. تدعم اللغة العربية والإنجليزية.
            استخدم المعلومات من قاعدة البيانات الطبية أولاً.""",
            
            'assistant': """أنت صيدلي وطبيب متخصص. تجيب بشكل مفصل ودقيق عن:
            - الأدوية والجرعات المناسبة
            - العلاجات والأعراض
            - العناية الصحية
            - منتجات الصيدلية
            
            أنت متخصص فقط في الطب والصيدلة. تدعم اللغة العربية والإنجليزية بطلاقة.""",
            
            'expert': """أنت خبير في الطب والصيدلة. تقدم إجابات دقيقة وتقنية مع:
            - معلومات طبية موثوقة
            - جرعات دقيقة
            - تحذيرات وموانع الاستخدام
            - نصائح طبية احترافية
            
            أنت متخصص فقط في الطب والصيدلة. تدعم العربية والإنجليزية."""
        }
        self.current_personality = 'default'
        
        self.analytics = {'total_users': 0, 'total_conversations': 0, 'total_processing_time': 0, 'last_updated': time.time()}
        self.models = {}

    def process_message(self, message: str, user_id: str, lang: Optional[str] = None, context: Dict = {}, image_data: Optional[str] = None, stream: bool = False):
        """Process incoming messages with advanced LLM, conversation memory, and RAG."""
        try:
            start = time.time()
            original_message = message
            preprocessed = preprocess_pipeline(message, lang)
            detected_lang = preprocessed.get('detected_lang', 'en')
            
            # Intent prediction (optional - لا يفشل إذا لم يكن متاحاً)
            try:
                if self.intent_recognizer:
                    intent_result = self.intent_recognizer.predict_intent(original_message)
                    intent = intent_result.get('intent', 'general')
                    confidence = intent_result.get('confidence', 0.8)
                else:
                    # Simple intent detection based on keywords
                    message_lower = original_message.lower()
                    if any(word in message_lower for word in ['منتج', 'product', 'شراء', 'buy', 'سعر', 'price']):
                        intent = 'product_inquiry'
                    elif any(word in message_lower for word in ['مشكلة', 'problem', 'علاج', 'treatment', 'حل', 'solution']):
                        intent = 'problem_solving'
                    elif any(word in message_lower for word in ['روتين', 'routine', 'استخدام', 'use', 'كيف', 'how']):
                        intent = 'routine_advice'
                    else:
                        intent = 'general'
                    confidence = 0.7
            except Exception as e:
                logger.debug(f"Intent prediction error: {e}")
                intent = 'general'
                confidence = 0.7
            
            # Sentiment analysis
            from nlp_preprocessing import analyze_sentiment
            sentiment_score, sentiment = analyze_sentiment(preprocessed['cleaned_text'])
            sent_conf = abs(sentiment_score)
            
            # Add user message to conversation memory (ChatGPT-like)
            if self.memory:
                self.memory.add_message(user_id, 'user', original_message, {
                    'intent': intent,
                    'sentiment': sentiment,
                    'lang': detected_lang
                })
            else:
                # Fallback to simple context
                if user_id not in self.context:
                    self.context[user_id] = []
                self.context[user_id].append({'message': original_message, 'intent': intent, 'sentiment': sentiment})
            
            ctx_summary = self.memory.get_context_summary(user_id) if self.memory else f"Recent context: {len(self.context.get(user_id, []))} messages"

            # --------------------------------------------------------------
            # 1) إعطاء أولوية للأسئلة الطبية: ابحث أولاً في قاعدة البيانات الطبية
            # --------------------------------------------------------------
            try:
                from database import search_medical_data, search_scraped_data

                medical_hits = search_medical_data(original_message, limit=3)
                if medical_hits:
                    # تنسيق نتائج طبية متخصصة وواضحة
                    parts = []
                    for i, item in enumerate(medical_hits, 1):
                        title = item.get('title', 'موضوع طبي')
                        category = item.get('category', 'medical')
                        content = (item.get('content') or '').strip()
                        if len(content) > 600:
                            content = content[:600] + '...'
                        dosage = item.get('dosage')
                        side_effects = item.get('side_effects')
                        contraindications = item.get('contraindications')

                        block = [f"{i}. {title} ({category})", ""]
                        if content:
                            block.append(content)
                        if dosage:
                            block.append(f"- الجرعة / Dosage: {dosage}")
                        if side_effects:
                            block.append(f"- الآثار الجانبية / Side effects: {side_effects}")
                        if contraindications:
                            block.append(f"- موانع الاستخدام / Contraindications: {contraindications}")
                        parts.append("\n".join(block))

                    disclaimer = (
                        "⚠️ هذه المعلومات تعليمية ولا تغني عن استشارة الطبيب أو الصيدلي.\n"
                        "Always consult a healthcare professional before using any medication or treatment."
                    )
                    response = "\n\n---\n\n".join(parts) + "\n\n" + disclaimer
                    return self._build_response(response, 'medical_info', sentiment, confidence, sent_conf, preprocessed, 0, start, user_id, detected_lang, original_message)

                # لو مفيش بيانات طبية مباشرة، جرّب البحث في البيانات المستخرجة من الروابط
                scraped_hits = search_scraped_data(original_message, limit=3)
                if scraped_hits:
                    parts = []
                    for i, item in enumerate(scraped_hits, 1):
                        title = item.get('title', 'معلومة طبية')
                        source = item.get('source', 'web')
                        snippet = (item.get('content') or '').strip()
                        if len(snippet) > 400:
                            snippet = snippet[:400] + '...'
                        parts.append(f"{i}. {title} [{source}]\n{snippet}")

                    response = "\n\n---\n\n".join(parts)
                    response += "\n\n💡 تم استخدام بيانات طبية محفوظة من مصادر سابقة للإجابة على سؤالك."
                    response += "\n⚠️ هذه المعلومات تعليمية ولا تغني عن استشارة الطبيب أو الصيدلي."
                    return self._build_response(response, 'medical_info', sentiment, confidence, sent_conf, preprocessed, 0, start, user_id, detected_lang, original_message)

            except Exception as med_err:
                logger.debug(f"Medical/local search in AdvancedChatbot failed: {med_err}")

            # Handle special commands first
            response = ""
            message_lower = original_message.lower()
            
            # التحقق من وجود روابط في الرسالة واستخراج البيانات منها
            scraper = get_web_scraper()
            urls = scraper.extract_urls(original_message)
            
            if urls:
                # استخدام ScraperManager للمعالجة المتقدمة
                from scraper_manager import get_scraper_manager
                scraper_manager = get_scraper_manager()
                
                # تحديد الأولويات بناءً على نوع الموقع
                def get_priority(url: str) -> int:
                    if 'webteb.com' in url or 'wikipedia.org' in url:
                        return 1  # أولوية عالية
                    elif 'medical' in url or 'health' in url:
                        return 3  # أولوية متوسطة-عالية
                    else:
                        return 5  # أولوية متوسطة
                
                priorities = [get_priority(url) for url in urls[:5]]  # معالجة أول 5 روابط
                
                # معالجة الروابط
                batch_result = scraper_manager.process_batch(
                    urls[:5], 
                    priorities=priorities,
                    force_refresh=False
                )
                
                # تجهيز الرد
                scraped_data_list = []
                successful_count = 0
                
                for result in batch_result.get('results', []):
                    if result.get('success'):
                        successful_count += 1
                        formatted_data = scraper.format_scraped_data(result)
                        scraped_data_list.append(formatted_data)
                        
                        # حفظ في Vector DB
                        url = result.get('url')
                        if self.vector_db and result.get('content'):
                            try:
                                content = result.get('content', '')
                                if len(content) > 1000:
                                    chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                                else:
                                    chunks = [content]
                                
                                texts = []
                                metadatas = []
                                for i, chunk in enumerate(chunks):
                                    texts.append(chunk)
                                    metadatas.append({
                                        'url': url,
                                        'title': result.get('title', ''),
                                        'source': result.get('source', 'web_scraper'),
                                        'chunk_index': i,
                                        'timestamp': time.time(),
                                        'user_id': user_id
                                    })
                                
                                self.vector_db.add_documents(texts=texts, metadatas=metadatas)
                                logger.info(f"Data added to vector DB for URL: {url}")
                            except Exception as e:
                                logger.error(f"Error adding to vector DB: {e}")
                    else:
                        error_msg = result.get('error', 'خطأ غير معروف')
                        url = result.get('url', 'رابط غير معروف')
                        scraped_data_list.append(f"❌ فشل استخراج البيانات من {url}: {error_msg}")
                
                if scraped_data_list:
                    response = "\n\n---\n\n".join(scraped_data_list)
                    response += f"\n\n✅ تم معالجة {successful_count} من {len(urls[:5])} روابط بنجاح!"
                    response += "\n\n💡 يمكنك الآن السؤال عن محتوى هذه الروابط."
                    
                    # إضافة معلومات إضافية
                    if batch_result.get('failed', 0) > 0:
                        response += f"\n⚠️ فشل {batch_result.get('failed')} رابط. يمكنك المحاولة مرة أخرى."
                    
                    return self._build_response(response, intent, sentiment, confidence, sent_conf, preprocessed, 0, start, user_id, detected_lang, original_message)
            
            # Handle translation if requested
            if "translate to" in message_lower or "ترجمة إلى" in message_lower:
                target_lang = original_message.split("translate to")[-1].strip().lower()[:2] if "translate to" in message_lower else original_message.split("ترجمة إلى")[-1].strip().lower()[:2]
                source_lang = detected_lang
                text_to_translate = original_message.split("translate to")[0].strip() if "translate to" in message_lower else original_message.split("ترجمة إلى")[0].strip()
                translated_text = translate_text(text_to_translate, source_lang, target_lang)
                response = f"Translated to {target_lang.upper()}: {translated_text}"
            
            # معالجة الصور
            elif image_data and ("edit image" in message_lower or "تعديل صورة" in message_lower):
                styled_image = apply_artistic_style(image_data, style="digital_art")
                response = f"Image edited with digital art style: <img src='data:image/png;base64,{styled_image}' style='max-width: 300px;'/>"
            
            # البحث في قاعدة المعرفة أولاً
            elif self.knowledge_base:
                # أوامر خاصة للمساعدة
                if message_lower in ['مساعدة', 'help', 'الأقسام', 'sections', 'المساعدة', 'أقسام', 'ماذا تعرف', 'what do you know']:
                    if self.knowledge_base:
                        sections = self.knowledge_base.get_all_sections()
                        response = "**الأقسام المتاحة في قاعدة المعرفة:**\n\n"
                        for i, section in enumerate(sections[:10], 1):  # أول 10 أقسام
                            response += f"{i}. {section}\n"
                        response += f"\n**إجمالي الأقسام:** {len(sections)}\n"
                        response += "\nيمكنك السؤال عن أي موضوع من هذه الأقسام!"
                    else:
                        response = "قاعدة المعرفة غير متاحة حالياً."
                    return self._build_response(response, intent, sentiment, confidence, sent_conf, preprocessed, 0, start, user_id, detected_lang, original_message)
            
                # الكلمات المفتاحية للبحث في قاعدة المعرفة
                ai_keywords = ['ذكاء', 'اصطناعي', 'تعلم', 'آلة', 'neural', 'ai', 'ml', 'deep learning', 
                              'machine learning', 'chatbot', 'transformers', 'nlp', 'computer vision',
                              'تعلم عميق', 'شبكة عصبية', 'معالجة', 'لغة', 'طبيعية', 'cnn', 'rnn', 
                              'lstm', 'bert', 'gpt', 'transformer', 'gan', 'reinforcement', 'تعزيز',
                              'محادثة', 'رؤية', 'حاسوبية', 'أخلاقيات', 'أمان', 'خوارزمية']
                
                # التحقق إذا كان السؤال متعلق بـ AI
                is_ai_question = any(keyword in message_lower for keyword in ai_keywords)
                
                if is_ai_question or any(keyword in preprocessed.get('keywords', []) for keyword in ai_keywords):
                    # البحث في قاعدة المعرفة
                    kb_answer = self.knowledge_base.get_answer(original_message)
                    if kb_answer and "لم أجد" not in kb_answer:
                        response = kb_answer
                    else:
                        # محاولة البحث بالكلمات المفتاحية
                        quick_info = self.knowledge_base.get_quick_info(original_message)
                        if quick_info:
                            response = quick_info
                        else:
                            # استخدام النموذج مع معلومات من قاعدة المعرفة
                            search_results = self.knowledge_base.search(original_message, max_results=1)
                            if search_results:
                                kb_context = search_results[0]['content'][:300]
                                if self.hf_pipeline:
                                    try:
                                        prompt = f"السؤال: {original_message}\nالمعلومات المتاحة: {kb_context}\n\nأجب بناءً على المعلومات المتاحة:"
                                        response = self.hf_pipeline(prompt, max_length=300)[0]['generated_text']
                                    except:
                                        response = f"{kb_context}\n\nهذه معلومات أولية. هل تريد المزيد من التفاصيل حول موضوع معين؟"
                                else:
                                    response = kb_context
                            else:
                                response = "أعتذر، لم أجد معلومات مباشرة حول هذا الموضوع في قاعدة المعرفة. هل يمكنك إعادة صياغة السؤال أو توضيح ما تريد معرفته؟"
                else:
                    # للأسئلة العامة، استخدام النموذج أو الرد الافتراضي
                    if self.hf_pipeline:
                        try:
                            prompt = f"Respond to in Arabic: {original_message}. Context: {ctx_summary}"
                            response = self.hf_pipeline(prompt, max_length=200)[0]['generated_text']
                        except Exception as e:
                            logger.error(f"Error generating response: {e}")
                            response = "أعتذر، حدث خطأ في معالجة رسالتك. يرجى المحاولة مرة أخرى."
                    else:
                        response = "مرحباً! كيف يمكنني مساعدتك اليوم؟"
            
            # البحث في الويب
            elif intent == 'search':
                from advanced_features import search_web
                results = search_web(preprocessed['cleaned_text'])
                response = f"Search results: {results[0]['title']}" if results else "No results found"
            
            # توليد الكود
            elif intent == 'generate_code':
                if self.hf_pipeline:
                    prompt = f"Generate {original_message} code"
                    response = self.hf_pipeline(prompt, max_length=200)[0]['generated_text']
                else:
                    response = "عذراً، ميزة توليد الكود غير متاحة حالياً."
            
            # Use LLM for ChatGPT-like responses (RAG-enhanced)
            # ALWAYS search web when local data not found
            else:
                # Generate LLM response - will search web automatically if no local data
                response = self._generate_llm_response(
                    user_id, original_message, detected_lang, 
                    ctx_summary, intent, sentiment, stream=stream, web_info=None
                )
            
            # Add assistant response to memory (ChatGPT-like)
            if self.memory and response:
                self.memory.add_message(user_id, 'assistant', response, {
                    'intent': intent,
                    'sentiment': sentiment,
                    'lang': detected_lang
                })
            
            # بناء الرد النهائي
            result = self._build_response(response, intent, sentiment, confidence, sent_conf, preprocessed, 0, start, user_id, detected_lang, original_message)
            
            # Save conversation periodically
            if self.memory:
                if self.analytics['total_conversations'] % 10 == 0:
                    self.memory.save_to_file('logs/conversations.pkl')
            
            return result
        
        except Exception as e:
            logger.error(f"Error in process_message: {e}")
            return {'response': 'عذراً، حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى.', 'detected_lang': 'ar'}
    
    def _generate_llm_response(self, user_id: str, message: str, lang: str, 
                              context_summary: str, intent: str, sentiment: str, 
                              stream: bool = False, web_info: Optional[str] = None) -> str:
        """Generate ChatGPT-like response using LLM with RAG"""
        try:
            # Get system prompt based on personality
            system_prompt = self.system_prompts.get(self.current_personality, self.system_prompts['default'])
            
            # Get conversation history (ChatGPT-like)
            if self.memory:
                messages = self.memory.get_formatted_messages(
                    user_id, 
                    system_prompt=system_prompt, 
                    limit=15  # Last 15 messages
                )
            else:
                # Fallback: create messages from scratch
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]
            
            # RAG: Enhance with knowledge base and vector database
            rag_context = ""
            
            # استخدام نظام RAG المحسّن
            try:
                from rag_enhancer import get_rag_enhancer
                rag_enhancer = get_rag_enhancer()
                enhanced_results = rag_enhancer.search_enhanced(message, limit=5)
                
                if enhanced_results:
                    rag_context = rag_enhancer.format_context(enhanced_results, max_length=2500)
                    if rag_context:
                        rag_context = "\n\n📚 معلومات من قاعدة المعرفة:\n" + rag_context
            except Exception as e:
                logger.debug(f"Enhanced RAG error, falling back to standard search: {e}")
            
            # Fallback: البحث القياسي إذا فشل النظام المحسّن
            if not rag_context:
                # 1. البحث في قاعدة البيانات الطبية والصيدلانية أولاً (الأولوية الأولى!)
                try:
                    from database import search_medical_data
                    medical_results = search_medical_data(message, limit=3)
                    
                    if medical_results:
                        rag_context += "\n\n💊 معلومات طبية وصيدلانية من قاعدة البيانات:\n"
                        for i, result in enumerate(medical_results[:3], 1):
                            title = result.get('title', 'بدون عنوان')
                            content = result.get('content', '')
                            dosage = result.get('dosage', '')
                            side_effects = result.get('side_effects', '')
                            contraindications = result.get('contraindications', '')
                            category = result.get('category', '')
                            score = result.get('relevance_score', 0)
                            
                            # إضافة علامة الجودة بناءً على درجة التطابق
                            quality_mark = "⭐" if score >= 5 else "📄"
                            
                            rag_context += f"{quality_mark} **{title}**"
                            if category:
                                rag_context += f" ({category})"
                            rag_context += f":\n{content}\n"
                            
                            if dosage:
                                rag_context += f"💉 **الجرعة:** {dosage}\n"
                            if side_effects:
                                rag_context += f"⚠️ **الآثار الجانبية:** {side_effects}\n"
                            if contraindications:
                                rag_context += f"🚫 **موانع الاستخدام:** {contraindications}\n"
                            rag_context += "\n"
                except Exception as e:
                    logger.debug(f"Medical data search error: {e}")
            
            # 2. البحث في قاعدة البيانات المستخرجة من الروابط (إذا لم توجد بيانات طبية)
            if not rag_context:
                try:
                    from database import search_scraped_data
                    from web_scraper_utils import get_data_manager
                    
                    # بحث بسيط أولاً
                    scraped_results = search_scraped_data(message, limit=5)
                    
                    # إذا لم توجد نتائج، جرب بحث متقدم
                    if not scraped_results:
                        data_manager = get_data_manager()
                        scraped_results = data_manager.search_advanced(
                            query=message,
                            min_content_length=100
                        )
                    
                    if scraped_results:
                        rag_context += "\n\n📚 معلومات من الروابط المحفوظة:\n"
                        for i, result in enumerate(scraped_results[:3], 1):
                            title = result.get('title', 'بدون عنوان')
                            content = result.get('content', '')[:400]
                            url = result.get('url', '')
                            source = result.get('source', '')
                            score = result.get('relevance_score', 0)
                            
                            # إضافة علامة الجودة بناءً على درجة التطابق
                            quality_mark = "⭐" if score >= 5 else "📄"
                            
                            rag_context += f"{quality_mark} **{title}**"
                            if source:
                                rag_context += f" ({source})"
                            rag_context += f": {content}\n"
                            if url:
                                rag_context += f"   🔗 {url}\n"
                            rag_context += "\n"
                except Exception as e:
                    logger.debug(f"Scraped data search error: {e}")
            
            # 3. إذا لم توجد نتائج محلية، ابحث في الإنترنت مباشرة (ALWAYS - دائماً!)
            if not rag_context:
                try:
                    from web_search_service import get_web_search_service
                    web_search = get_web_search_service()
                    
                    # البحث في الإنترنت - دائماً عندما لا توجد بيانات محلية
                    logger.info(f"🔍 No local data found, searching web for: {message}")
                    web_results = web_search.search_and_scrape(message, max_results=5)
                    
                    if web_results:
                        rag_context += "\n\n🌐 معلومات محدثة من الإنترنت:\n"
                        for i, result in enumerate(web_results[:5], 1):
                            title = result.get('title', 'بدون عنوان')
                            content = result.get('content', '')[:500] or result.get('description', '')[:500]
                            url = result.get('url', '')
                            
                            rag_context += f"🌐 **{title}**\n"
                            if content:
                                rag_context += f"{content}\n"
                            if url:
                                rag_context += f"🔗 {url}\n"
                            rag_context += "\n"
                        
                        # حفظ النتائج في قاعدة البيانات للاستخدام المستقبلي
                        try:
                            from database import save_scraped_data
                            from scraper_manager import get_scraper_manager
                            
                            scraper_manager = get_scraper_manager()
                            for result in web_results:
                                if result.get('url'):
                                    scraper_manager.add_url(
                                        url=result['url'],
                                        priority=5,
                                        force_refresh=False
                                    )
                        except Exception as e:
                            logger.debug(f"Failed to save web results: {e}")
                    else:
                        # إذا فشل search_and_scrape، جرب بحث بسيط
                        logger.info(f"🔍 Trying simple web search for: {message}")
                        simple_results = web_search.search_web(message, max_results=5)
                        if simple_results:
                            rag_context += "\n\n🌐 معلومات من الإنترنت:\n"
                            for i, result in enumerate(simple_results[:5], 1):
                                title = result.get('title', 'بدون عنوان')
                                snippet = result.get('snippet', '')[:500]
                                url = result.get('url', '')
                                
                                rag_context += f"🌐 **{title}**\n"
                                if snippet:
                                    rag_context += f"{snippet}\n"
                                if url:
                                    rag_context += f"🔗 {url}\n"
                                rag_context += "\n"
                            
                except Exception as e:
                    logger.warning(f"Web search error: {e}", exc_info=True)
            
            # Try vector database (semantic search) - أفضل للبحث الدلالي (محسّن)
            if self.vector_db:
                try:
                    # زيادة عدد النتائج للبحث الدلالي
                    vector_results = self.vector_db.search(message, k=7)
                    if vector_results:
                        if not rag_context:
                            rag_context = "\n\n🔍 معلومات ذات صلة (من البحث الدلالي):\n"
                        else:
                            rag_context += "\n\n🔍 معلومات إضافية من البحث الدلالي:\n"
                        
                        seen_urls = set()
                        for result in vector_results:
                            text = result.get('text', '')[:350]
                            metadata = result.get('metadata', {})
                            title = metadata.get('title', '')
                            url = metadata.get('url', '')
                            source = metadata.get('source', '')
                            score = result.get('score', 0)
                            
                            # تجنب التكرار
                            if url and url in seen_urls:
                                continue
                            seen_urls.add(url)
                            
                            # فلترة بناءً على درجة التطابق
                            if score < 0.3:  # تجاهل النتائج ضعيفة التطابق
                                continue
                            
                            quality_mark = "⭐" if score >= 0.7 else "📄"
                            
                            if url:
                                rag_context += f"{quality_mark} **{title}**"
                                if source:
                                    rag_context += f" ({source})"
                                rag_context += f": {text}\n"
                                rag_context += f"   🔗 {url}\n\n"
                            else:
                                rag_context += f"{quality_mark} {text}\n\n"
                except Exception as e:
                    logger.debug(f"Vector DB search error: {e}")
            
            # 3. Fallback to knowledge base (آخر خيار - فقط إذا لم توجد نتائج من الإنترنت)
            if not rag_context and self.knowledge_base:
                try:
                    kb_results = self.knowledge_base.search(message, max_results=2)
                    if kb_results:
                        rag_context = "\n\nمعلومات إضافية من قاعدة المعرفة:\n"
                        for result in kb_results:
                            rag_context += f"- {result['content'][:200]}\n"
                except Exception as e:
                    logger.debug(f"Knowledge base search error: {e}")
            
            # 4. إذا لم توجد أي معلومات، ابحث في الإنترنت مرة أخرى (fallback نهائي)
            if not rag_context:
                try:
                    from web_search_service import get_web_search_service
                    web_search = get_web_search_service()
                    
                    # بحث بسيط في الإنترنت
                    simple_results = web_search.search_web(message, max_results=2)
                    if simple_results:
                        rag_context = "\n\n🌐 معلومات من الإنترنت:\n"
                        for result in simple_results:
                            title = result.get('title', '')
                            snippet = result.get('snippet', '')
                            url = result.get('url', '')
                            
                            if title or snippet:
                                rag_context += f"🌐 **{title}**\n"
                                rag_context += f"{snippet}\n"
                                if url:
                                    rag_context += f"   🔗 {url}\n"
                                rag_context += "\n"
                except Exception as e:
                    logger.debug(f"Final web search error: {e}")
            
            # Add web_info if provided (from process_message)
            if web_info:
                if not rag_context:
                    rag_context = web_info
                else:
                    rag_context = web_info + "\n" + rag_context
            
            # Add RAG context to system prompt
            if rag_context and messages and messages[0]['role'] == 'system':
                messages[0]['content'] += rag_context
            
            # Try LLM Manager first (OpenAI, HuggingFace, Ollama)
            # Use caching for non-streaming responses
            cache_key = None
            if not stream and self.advanced_cache:
                # Generate cache key from messages
                import hashlib
                messages_str = str(messages)
                cache_key = f"llm_response_{hashlib.md5(messages_str.encode()).hexdigest()}"
                
                # Try to get from cache
                cached_response = self.advanced_cache.get(cache_key)
                if cached_response:
                    logger.debug("Using cached LLM response")
                    return cached_response
            
            if self.llm_manager:
                try:
                    if stream:
                        # Streaming response (ChatGPT-like)
                        full_response = ""
                        for token in self.llm_manager.stream_generate(messages):
                            full_response += token
                        return full_response
                    else:
                        # Regular response
                        result = self.llm_manager.generate(messages)
                        if 'content' in result:
                            response_content = result['content']
                            
                            # Cache the response
                            if cache_key and self.advanced_cache:
                                self.advanced_cache.set(cache_key, response_content, ttl=3600)
                            
                            return response_content
                        else:
                            logger.warning(f"LLM result missing content: {result}")
                except Exception as e:
                    logger.error(f"LLM Manager error: {e}")
                    # Fallback to next method
            
            # Fallback: Try HuggingFace pipeline
            if self.hf_pipeline:
                try:
                    # Build enhanced prompt
                    prompt_parts = [
                        f"السؤال: {message}",
                        f"السياق: {context_summary}",
                        f"النية: {intent}",
                        f"المشاعر: {sentiment}"
                    ]
                    if rag_context:
                        prompt_parts.append(rag_context)
                    
                    prompt = "\n".join(prompt_parts) + "\n\nأجب بشكل مفيد وواضح:"
                    result = self.hf_pipeline(prompt, max_length=500, num_return_sequences=1)
                    if result and len(result) > 0:
                        return result[0].get('generated_text', '')
                except Exception as e:
                    logger.error(f"HuggingFace pipeline error: {e}")
            
            # Final fallback: Use web search if nothing else worked
            if not rag_context:
                try:
                    from web_search_service import get_web_search_service
                    web_search = get_web_search_service()
                    if web_search:
                        # Last resort: simple web search
                        simple_results = web_search.search_web(message, max_results=2)
                        if simple_results:
                            if lang == 'ar':
                                response_text = "🌐 وجدت المعلومات التالية:\n\n"
                            else:
                                response_text = "🌐 I found the following information:\n\n"
                            
                            for result in simple_results:
                                title = result.get('title', '')
                                snippet = result.get('snippet', '')
                                url = result.get('url', '')
                                
                                if title:
                                    response_text += f"**{title}**\n"
                                if snippet:
                                    response_text += f"{snippet}\n"
                                if url:
                                    response_text += f"🔗 {url}\n"
                                response_text += "\n"
                            
                            return response_text
                except Exception as e:
                    logger.debug(f"Final web search fallback error: {e}")
            
            # Use knowledge base if available
            if self.knowledge_base:
                kb_answer = self.knowledge_base.get_answer(message)
                if kb_answer and "لم أجد" not in kb_answer:
                    return kb_answer
            
            # Smart default response based on language
            if lang == 'ar':
                return f"شكراً لسؤالك! '{message}'. أنا أبحث في الإنترنت للحصول على أحدث المعلومات. هل يمكنك توضيح سؤالك أكثر لأقدم لك إجابة أدق وأكثر تفصيلاً؟"
            else:
                return f"Thank you for your question! '{message}'. I'm searching the web for the latest information. Could you clarify your question more so I can provide a more accurate and detailed answer?"
                
        except Exception as e:
            logger.error(f"Error in _generate_llm_response: {e}")
            return "عذراً، حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى."
    
    def _build_response(self, response: str, intent: str, sentiment: str, confidence: float, 
                       sent_conf: float, preprocessed: Dict, processing_time: float, 
                       start: float, user_id: str, detected_lang: str, message: str = "") -> Dict:
        """بناء الرد النهائي وحفظه في قاعدة البيانات"""
        try:
            if processing_time == 0:
                processing_time = time.time() - start
            
            self.analytics['total_conversations'] += 1
            self.analytics['total_processing_time'] += processing_time
            if user_id not in self.context:
                self.analytics['total_users'] += 1
            self.analytics['last_updated'] = time.time()

            from database import save_conversation, update_analytics
            from datetime import datetime
            msg = message if message else "Unknown"
            save_conversation(user_id, msg, response, intent, sentiment, confidence, datetime.utcnow())
            update_analytics(self.analytics['total_users'], self.analytics['total_conversations'], processing_time)

            logger.info(f"Processed message for {user_id}: Intent={intent}, Lang={detected_lang}")

            return {
                'response': response,
                'intent': intent,
                'intent_confidence': confidence,
                'sentiment': sentiment,
                'sentiment_confidence': sent_conf,
                'entities': preprocessed.get('entities', []),
                'keywords': preprocessed.get('keywords', []),
                'context_summary': preprocessed.get('context_summary', ''),
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat(),
                'detected_lang': detected_lang
            }
        except Exception as e:
            logger.error(f"Error in _build_response: {e}")
            return {
                'response': response,
                'intent': intent,
                'detected_lang': detected_lang
            }

    def stream_response(self, message: str, user_id: str, lang: Optional[str] = None) -> Iterator[str]:
        """Stream response tokens (ChatGPT-like streaming)"""
        try:
            # Process message with streaming
            preprocessed = preprocess_pipeline(message, lang)
            detected_lang = preprocessed.get('detected_lang', 'en')
            
            # Add to memory
            if self.memory:
                self.memory.add_message(user_id, 'user', message)
            
            # Get system prompt
            system_prompt = self.system_prompts.get(self.current_personality, self.system_prompts['default'])
            
            # Get messages
            if self.memory:
                messages = self.memory.get_formatted_messages(user_id, system_prompt=system_prompt, limit=15)
            else:
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]
            
            # Stream from LLM
            if self.llm_manager:
                full_response = ""
                for token in self.llm_manager.stream_generate(messages):
                    full_response += token
                    yield token
                
                # Save to memory after streaming
                if self.memory:
                    self.memory.add_message(user_id, 'assistant', full_response)
            else:
                yield "Streaming not available. Please use regular response."
                
        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            yield f"Error: {str(e)}"
    
    def set_personality(self, personality: str):
        """Set chatbot personality (default, assistant, expert)"""
        if personality in self.system_prompts:
            self.current_personality = personality
            logger.info(f"Personality changed to: {personality}")
        else:
            logger.warning(f"Unknown personality: {personality}")
    
    def clear_conversation(self, user_id: str):
        """Clear conversation history for a user"""
        if self.memory:
            self.memory.clear_conversation(user_id)
        if user_id in self.context:
            del self.context[user_id]
        logger.info(f"Conversation cleared for user: {user_id}")
    
    def train_models(self, data: Dict, configs: Dict) -> Dict[str, Any]:
        """Train NLP models with provided data and configurations."""
        try:
            from model_training import train_models
            models = train_models(data, configs)
            self.models.update(models)
            logger.info("Models trained and updated successfully.")
            return {'status': 'success', 'models': list(models.keys())}
        except Exception as e:
            logger.error(f"Error in train_models: {e}")
            raise