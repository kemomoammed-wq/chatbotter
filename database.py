# database.py: Database management with SQLAlchemy for conversation and analytics tracking
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Optional, List, Any
from datetime import datetime as dt, timezone
import logging
import json
import os
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO, filename='logs/chatbot.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

# ---------------------------------------------------------------------------
# Database configuration: prefer SQL Server instance DESKTOP-EETM136\SQLEXPRESS
# ---------------------------------------------------------------------------
def _build_engine():
    """
    Create SQLAlchemy engine.
    Priority:
    1) Explicit DB_URL env var.
    2) Local SQL Server instance DESKTOP-EETM136\SQLEXPRESS (trusted connection).
    3) Fallback to local SQLite.
    """
    env_url = os.getenv("DB_URL")
    if env_url:
        logger.info("Using DB_URL from environment")
        return create_engine(env_url, pool_size=10, max_overflow=20, fast_executemany=True)

    # Default SQL Server connection (Windows authentication)
    try:
        driver = os.getenv("DB_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
        server = os.getenv("DB_SERVER", r"DESKTOP-EETM136\SQLEXPRESS")
        database = os.getenv("DB_NAME", "chatbot")

        sql_server_url = (
            f"mssql+pyodbc://@{server}/{database}"
            f"?driver={quote_plus(driver)}"
            f"&trusted_connection=yes"
        )
        logger.info(f"Using default SQL Server at {server} / database {database}")
        return create_engine(sql_server_url, pool_size=10, max_overflow=20, fast_executemany=True)
    except Exception as exc:
        logger.warning(f"SQL Server engine init failed, falling back to SQLite: {exc}")
        return create_engine('sqlite:///logs/chatbot.db', pool_size=10, max_overflow=20)


engine = _build_engine()
Session = sessionmaker(bind=engine)

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    intent = Column(String)
    sentiment = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=lambda: dt.now(timezone.utc))

class Analytics(Base):
    __tablename__ = 'analytics'
    id = Column(Integer, primary_key=True)
    total_users = Column(Integer, default=0)
    total_conversations = Column(Integer, default=0)
    avg_processing_time = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), default=lambda: dt.now(timezone.utc))

class ScrapedData(Base):
    __tablename__ = 'scraped_data'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String)
    description = Column(Text)
    content = Column(Text)
    source = Column(String)  # 'webteb', 'general', etc.
    extra_data = Column(Text)  # JSON string for additional data (renamed from metadata)
    timestamp = Column(DateTime(timezone=True), default=lambda: dt.now(timezone.utc))

class MedicalData(Base):
    """قاعدة بيانات طبية وصيدلانية متخصصة"""
    __tablename__ = 'medical_data'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)  # عنوان الموضوع (مثل: دواء الباراسيتامول)
    category = Column(String)  # 'pharmacy', 'medicine', 'treatment', 'symptom', 'disease'
    keywords = Column(Text)  # كلمات مفتاحية للبحث (مفصولة بفواصل)
    content = Column(Text, nullable=False)  # المحتوى الطبي الكامل
    dosage = Column(Text)  # الجرعات (إن وجدت)
    side_effects = Column(Text)  # الآثار الجانبية
    contraindications = Column(Text)  # موانع الاستخدام
    source = Column(String)  # المصدر (مثل: 'doctor', 'pharmacy', 'manual')
    timestamp = Column(DateTime(timezone=True), default=lambda: dt.now(timezone.utc))

class TrainingSample(Base):
    """عينات تدريبية لحفظ الرسائل، الردود، وبيانات البحث."""
    __tablename__ = 'training_samples'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, default='anonymous')
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    search_results = Column(Text)  # JSON string of search hits
    tags = Column(String)  # comma-separated tags
    timestamp = Column(DateTime(timezone=True), default=lambda: dt.now(timezone.utc))

class User(Base):
    """جدول المستخدمين"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)  # الاسم الكامل
    language = Column(String, default='ar')  # اللغة المفضلة
    created_at = Column(DateTime(timezone=True), default=lambda: dt.now(timezone.utc))
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive

# Initialize database
Base.metadata.create_all(engine)

# إضافة بعض البيانات الطبية الأساسية عند أول تشغيل
def initialize_default_medical_data():
    """إضافة بيانات طبية أساسية"""
    try:
        session = Session()
        # التحقق من وجود بيانات
        existing = session.query(MedicalData).first()
        if existing:
            logger.info("Medical data already exists, skipping initialization")
            session.close()
            return
        
        # بيانات أساسية
        default_data = [
            {
                'title': 'الباراسيتامول (Paracetamol)',
                'category': 'pharmacy',
                'keywords': 'باراسيتامول, باراسيتامول, مسكن, خافض حرارة, ألم, صداع, حرارة',
                'content': 'الباراسيتامول هو دواء مسكن للآلام وخافض للحرارة. يستخدم لعلاج الصداع، آلام الأسنان، آلام العضلات، والحمى. الجرعة المعتادة للبالغين: 500-1000 مجم كل 4-6 ساعات، بحد أقصى 4000 مجم يومياً.',
                'dosage': 'البالغين: 500-1000 مجم كل 4-6 ساعات. الأطفال: حسب الوزن (10-15 مجم/كجم)',
                'side_effects': 'نادراً ما يسبب آثار جانبية. الجرعات الزائدة قد تسبب تلف الكبد.',
                'contraindications': 'لا يستخدم في حالات الفشل الكبدي الشديد. تجنب مع الكحول.',
                'source': 'pharmacy'
            },
            {
                'title': 'تنعيم الشعر',
                'category': 'treatment',
                'keywords': 'شعر, تنعيم, نعومة, علاج الشعر, منتجات الشعر, العناية بالشعر',
                'content': 'لتنعيم الشعر يمكن استخدام: 1) شامبو وبلسم للشعر الجاف 2) زيوت طبيعية مثل زيت الأرجان أو زيت جوز الهند 3) ماسكات الشعر الطبيعية 4) تجنب الحرارة العالية والتجفيف المفرط. استخدم منتجات خالية من الكبريتات.',
                'dosage': None,
                'side_effects': 'قد يسبب حساسية في بعض الأشخاص',
                'contraindications': 'تجنب في حالة الحساسية للمكونات',
                'source': 'pharmacy'
            }
        ]
        
        for data in default_data:
            medical = MedicalData(**data)
            session.add(medical)
        
        session.commit()
        logger.info(f"Initialized {len(default_data)} default medical data entries")
        session.close()
    except Exception as e:
        logger.error(f"Error initializing medical data: {e}")
        try:
            session.rollback()
            session.close()
        except:
            pass

# تهيئة البيانات عند الاستيراد
try:
    initialize_default_medical_data()
except Exception as e:
    logger.warning(f"Could not initialize medical data: {e}")

def save_conversation(user_id: str, message: str, response: str, intent: str, sentiment: str, confidence: float, timestamp: Optional[dt] = None) -> None:
    """Save a conversation entry to the database."""
    try:
        session = Session()
        if timestamp is None:
            timestamp = dt.now(timezone.utc)
        elif isinstance(timestamp, str):
            # Convert string to datetime if needed
            try:
                timestamp = dt.fromisoformat(timestamp.replace('Z', '+00:00'))
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
            except:
                timestamp = dt.now(timezone.utc)
        conv = Conversation(user_id=user_id, message=message, response=response, intent=intent, sentiment=sentiment, confidence=confidence, timestamp=timestamp)
        session.add(conv)
        session.commit()
        logger.info(f"Conversation saved for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        session.rollback()
    finally:
        session.close()

def save_training_sample(user_id: str, message: str, response: str, search_results: Optional[List[Dict]] = None, tags: Optional[List[str]] = None, timestamp: Optional[dt] = None, intent: Optional[str] = None, sentiment: Optional[str] = None, confidence: Optional[float] = None) -> None:
    """حفظ عينة تدريبية محسّنة تتضمن نتائج البحث وبيانات إضافية للتدريب."""
    try:
        session = Session()
        ts = timestamp or dt.now(timezone.utc)
        
        # تحسين البيانات المخزنة
        enhanced_data = {
            "search_results": search_results or [],
            "search_count": len(search_results) if search_results else 0,
            "intent": intent,
            "sentiment": sentiment,
            "confidence": confidence,
            "message_length": len(message),
            "response_length": len(response),
            "has_web_results": bool(search_results and len(search_results) > 0)
        }
        
        sample = TrainingSample(
            user_id=user_id or 'anonymous',
            message=message,
            response=response,
            search_results=json.dumps(enhanced_data, ensure_ascii=False),
            tags=",".join(tags) if tags else None,
            timestamp=ts
        )
        session.add(sample)
        session.commit()
        logger.info(f"✅ Training sample saved for user {user_id} (search_results: {len(search_results) if search_results else 0})")
    except Exception as e:
        logger.error(f"❌ Error saving training sample: {e}", exc_info=True)
        session.rollback()
    finally:
        session.close()

def update_analytics(total_users: int, total_conversations: int, avg_time: float) -> None:
    """Update analytics data in the database."""
    try:
        session = Session()
        analytics = session.query(Analytics).first()
        if not analytics:
            analytics = Analytics(total_users=total_users, total_conversations=total_conversations, avg_processing_time=avg_time)
            session.add(analytics)
        else:
            analytics.total_users = total_users
            analytics.total_conversations = total_conversations
            analytics.avg_processing_time = avg_time
            analytics.last_updated = dt.now(timezone.utc)
        session.commit()
        logger.info("Analytics updated successfully")
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")
        session.rollback()
    finally:
        session.close()

def get_analytics() -> Dict[str, Any]:
    """Retrieve current analytics data."""
    try:
        session = Session()
        analytics = session.query(Analytics).first()
        return {
            'total_users': analytics.total_users if analytics else 0,
            'total_conversations': analytics.total_conversations if analytics else 0,
            'avg_processing_time': analytics.avg_processing_time if analytics else 0.0,
            'last_updated': analytics.last_updated.isoformat() if analytics and analytics.last_updated else dt.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}")
        return {}
    finally:
        session.close()

def get_conversations(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """استرجاع آخر المحادثات من قاعدة البيانات."""
    session = Session()
    try:
        query = session.query(Conversation).order_by(Conversation.timestamp.desc())
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        rows = query.limit(limit).all()
        return [
            {
                "id": row.id,
                "user_id": row.user_id,
                "message": row.message,
                "response": row.response,
                "intent": row.intent,
                "sentiment": row.sentiment,
                "confidence": row.confidence,
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return []
    finally:
        session.close()

def get_training_samples(user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """استرجاع عينات التدريب المخزنة (رسائل + نتائج البحث)."""
    session = Session()
    try:
        query = session.query(TrainingSample).order_by(TrainingSample.timestamp.desc())
        if user_id:
            query = query.filter(TrainingSample.user_id == user_id)
        rows = query.limit(limit).all()
        return [
            {
                "id": row.id,
                "user_id": row.user_id,
                "message": row.message,
                "response": row.response,
                "search_results": json.loads(row.search_results) if row.search_results else [],
                "tags": row.tags.split(",") if row.tags else [],
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching training samples: {e}")
        return []
    finally:
        session.close()

def save_scraped_data(url: str, title: str = None, description: str = None, content: str = None, 
                      source: str = None, metadata: Dict = None) -> bool:
    """حفظ البيانات المستخرجة من الروابط في قاعدة البيانات"""
    try:
        session = Session()
        # التحقق من وجود الرابط مسبقاً
        existing = session.query(ScrapedData).filter_by(url=url).first()
        
        if existing:
            # تحديث البيانات الموجودة
            if title:
                existing.title = title
            if description:
                existing.description = description
            if content:
                existing.content = content
            if source:
                existing.source = source
            if metadata:
                existing.extra_data = json.dumps(metadata, ensure_ascii=False)
            existing.timestamp = dt.now(timezone.utc)
        else:
            # إضافة بيانات جديدة
            scraped = ScrapedData(
                url=url,
                title=title or '',
                description=description or '',
                content=content or '',
                source=source or 'general',
                extra_data=json.dumps(metadata or {}, ensure_ascii=False)
            )
            session.add(scraped)
        
        session.commit()
        logger.info(f"Scraped data saved for URL: {url}")
        return True
    except Exception as e:
        logger.error(f"Error saving scraped data: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_scraped_data(url: str = None, source: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """استرجاع البيانات المستخرجة من قاعدة البيانات"""
    try:
        session = Session()
        query = session.query(ScrapedData)
        
        if url:
            query = query.filter_by(url=url)
        if source:
            query = query.filter_by(source=source)
        
        results = query.order_by(ScrapedData.timestamp.desc()).limit(limit).all()
        
        data_list = []
        for result in results:
            data_list.append({
                'id': result.id,
                'url': result.url,
                'title': result.title,
                'description': result.description,
                'content': result.content,
                'source': result.source,
                'metadata': json.loads(result.extra_data) if result.extra_data else {},
                'timestamp': result.timestamp.isoformat() if result.timestamp else None
            })
        
        return data_list
    except Exception as e:
        logger.error(f"Error retrieving scraped data: {e}")
        return []
    finally:
        session.close()

def search_scraped_data(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """البحث في البيانات المستخرجة"""
    try:
        session = Session()
        query_lower = query.lower()
        
        # تقسيم الكلمات للبحث المتقدم
        words = query_lower.split()
        
        # البحث في العنوان والوصف والمحتوى
        if len(words) == 1:
            # بحث بسيط
            results = session.query(ScrapedData).filter(
                (ScrapedData.title.contains(query_lower)) |
                (ScrapedData.description.contains(query_lower)) |
                (ScrapedData.content.contains(query_lower))
            ).limit(limit).all()
        else:
            # بحث متقدم - يجب أن تحتوي على جميع الكلمات
            from sqlalchemy import and_
            conditions = []
            for word in words:
                conditions.append(
                    (ScrapedData.title.contains(word)) |
                    (ScrapedData.description.contains(word)) |
                    (ScrapedData.content.contains(word))
                )
            results = session.query(ScrapedData).filter(
                and_(*conditions)
            ).limit(limit).all()
        
        data_list = []
        for result in results:
            # حساب درجة التطابق
            score = 0
            title_lower = (result.title or '').lower()
            desc_lower = (result.description or '').lower()
            content_lower = (result.content or '').lower()
            
            for word in words:
                if word in title_lower:
                    score += 3  # العنوان له وزن أكبر
                if word in desc_lower:
                    score += 2
                if word in content_lower:
                    score += 1
            
            data_list.append({
                'id': result.id,
                'url': result.url,
                'title': result.title,
                'description': result.description,
                'content': result.content[:500] if result.content else '',  # أول 500 حرف
                'source': result.source,
                'metadata': json.loads(result.extra_data) if result.extra_data else {},
                'timestamp': result.timestamp.isoformat() if result.timestamp else None,
                'relevance_score': score
            })
        
        # ترتيب حسب درجة التطابق
        data_list.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return data_list[:limit]
    except Exception as e:
        logger.error(f"Error searching scraped data: {e}")
        return []
    finally:
        session.close()

def save_medical_data(title: str, content: str, category: str = 'medicine', 
                     keywords: str = '', dosage: str = None, 
                     side_effects: str = None, contraindications: str = None,
                     source: str = 'manual') -> bool:
    """حفظ بيانات طبية/صيدلانية في قاعدة البيانات"""
    try:
        session = Session()
        medical = MedicalData(
            title=title,
            category=category,
            keywords=keywords,
            content=content,
            dosage=dosage,
            side_effects=side_effects,
            contraindications=contraindications,
            source=source
        )
        session.add(medical)
        session.commit()
        logger.info(f"Medical data saved: {title}")
        return True
    except Exception as e:
        logger.error(f"Error saving medical data: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def search_medical_data(query: str, category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
    """البحث في قاعدة البيانات الطبية والصيدلانية - الأولوية الأولى!"""
    try:
        session = Session()
        query_lower = query.lower()
        words = query_lower.split()
        
        # بناء استعلام البحث
        search_query = session.query(MedicalData)
        
        # فلترة حسب الفئة إذا تم تحديدها
        if category:
            search_query = search_query.filter(MedicalData.category == category)
        
        # البحث في العنوان والمحتوى والكلمات المفتاحية
        conditions = []
        for word in words:
            conditions.append(
                (MedicalData.title.contains(word)) |
                (MedicalData.content.contains(word)) |
                (MedicalData.keywords.contains(word))
            )
        
        if conditions:
            from sqlalchemy import or_
            search_query = search_query.filter(or_(*conditions))
        
        results = search_query.order_by(MedicalData.timestamp.desc()).limit(limit * 2).all()
        
        # حساب درجة التطابق وترتيب النتائج
        data_list = []
        for result in results:
            score = 0
            title_lower = (result.title or '').lower()
            content_lower = (result.content or '').lower()
            keywords_lower = (result.keywords or '').lower()
            
            for word in words:
                if word in title_lower:
                    score += 5  # العنوان له وزن كبير جداً
                if word in keywords_lower:
                    score += 4  # الكلمات المفتاحية مهمة
                if word in content_lower:
                    score += 1
            
            data_list.append({
                'id': result.id,
                'title': result.title,
                'category': result.category,
                'content': result.content,
                'dosage': result.dosage,
                'side_effects': result.side_effects,
                'contraindications': result.contraindications,
                'source': result.source,
                'relevance_score': score
            })
        
        # ترتيب حسب درجة التطابق
        data_list.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return data_list[:limit]
    except Exception as e:
        logger.error(f"Error searching medical data: {e}")
        return []
    finally:
        session.close()

def get_all_medical_data(category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """الحصول على جميع البيانات الطبية"""
    try:
        session = Session()
        query = session.query(MedicalData)
        
        if category:
            query = query.filter(MedicalData.category == category)
        
        results = query.order_by(MedicalData.timestamp.desc()).limit(limit).all()
        
        data_list = []
        for result in results:
            data_list.append({
                'id': result.id,
                'title': result.title,
                'category': result.category,
                'content': result.content[:200],  # أول 200 حرف
                'source': result.source
            })
        
        return data_list
    except Exception as e:
        logger.error(f"Error getting medical data: {e}")
        return []
    finally:
        session.close()