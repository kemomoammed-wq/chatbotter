"""
FastAPI server that mirrors the chatbot API and serves the React build.
Provides:
- /api/chat: processes messages, performs live web search, and stores training samples.
- /api/search: returns web search + scrape results.
- /api/health: simple health check.
"""

import logging
import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from youtube_service import YoutubeVideo, search_youtube_video

# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/chatbot.log", encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# React build directory
REACT_BUILD_DIR = os.path.join(os.path.dirname(__file__), "eva-wise-chat-buddy-main", "dist")
REACT_BUILD_EXISTS = os.path.exists(REACT_BUILD_DIR)

# Core systems
from core_integration import get_core_integration, get_chatbot, is_system_ready
from web_search_service import get_web_search_service

logger.info("Initializing Core Integration System (FastAPI)...")
try:
    core = get_core_integration()
    chatbot = get_chatbot()
    web_search = get_web_search_service()
    CHATBOT_LOADED = is_system_ready()
    logger.info(f"✅ Core systems initialized. Chatbot loaded: {CHATBOT_LOADED}")
except Exception as e:
    logger.error(f"❌ Error initializing core systems: {e}", exc_info=True)
    # Fallback - create minimal instances
    core = None
    chatbot = None
    web_search = None
    CHATBOT_LOADED = False
    logger.warning("⚠️ Running in fallback mode - some features may not work")

# Database helpers
try:
    from database import (
        save_conversation,
        save_training_sample,
        get_conversations,
        get_training_samples,
    )

    DB_AVAILABLE = core is not None and core.get_database() is not None
except Exception as exc:  # pragma: no cover - defensive fallback
    logger.warning(f"Database unavailable in FastAPI app: {exc}")
    DB_AVAILABLE = False

    def save_conversation(*args: Any, **kwargs: Any) -> None:
        logger.debug("Database unavailable, skipping save_conversation")

    def save_training_sample(*args: Any, **kwargs: Any) -> None:
        logger.debug("Database unavailable, skipping save_training_sample")

# Auto-load training data on startup
def load_training_data_on_startup():
    """تحميل بيانات التدريب تلقائياً عند بدء السيرفر"""
    try:
        from database import Session, ScrapedData, MedicalData, Conversation
        
        session = Session()
        try:
            # التحقق من وجود بيانات تدريب
            scraped_count = session.query(ScrapedData).count()
            medical_count = session.query(MedicalData).count()
            conversation_count = session.query(Conversation).filter(
                Conversation.user_id.like('training-%')
            ).count()
            
            # إذا كانت البيانات موجودة (أكثر من 5 عناصر)، لا نضيفها مرة أخرى
            if scraped_count > 5 and medical_count > 2 and conversation_count > 5:
                logger.info(f"✅ Training data already exists: {scraped_count} scraped, {medical_count} medical, {conversation_count} conversations")
                return False
            
            logger.info("📚 Loading training data automatically...")
            logger.info(f"   Current: {scraped_count} scraped, {medical_count} medical, {conversation_count} conversations")
            
            # استدعاء دالة إضافة بيانات التدريب
            try:
                from add_training_data import add_training_data
                add_training_data()
                logger.info("✅ Training data loaded successfully!")
                return True
            except ImportError:
                logger.warning("⚠️  add_training_data module not found, skipping auto-load")
                return False
            except Exception as e:
                logger.error(f"❌ Error loading training data: {e}", exc_info=True)
                return False
        finally:
            session.close()
    except Exception as e:
        logger.warning(f"⚠️  Could not check/load training data: {e}")
        return False

# تحميل بيانات التدريب عند بدء السيرفر
if DB_AVAILABLE:
    load_training_data_on_startup()
else:
    logger.info("⚠️  Database not available, skipping training data auto-load")


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    language: Optional[str] = None  # 'ar' | 'en'
    conversation_mode: Optional[str] = "smart"


AR_VIDEO_KEYWORDS = ["فيديو شرح", "شرح فيديو", "فيديو تعليمي"]
EN_VIDEO_KEYWORDS = ["video tutorial", "tutorial video", "explain in video"]


def extract_video_query(user_message: str) -> Optional[str]:
    """
    اكتشاف نية طلب \"فيديو شرح\" واستخراج موضوع البحث من رسالة المستخدم.
    أمثلة:
    - \"عايز فيديو شرح للـ FastAPI\" -> \"FastAPI\"
    - \"فيديو شرح عن الذكاء الاصطناعي\" -> \"الذكاء الاصطناعي\"
    إذا لم يتم اكتشاف نية فيديو، ترجع None.
    """
    text = (user_message or "").strip()
    if not text:
        return None

    lower = text.lower()

    # أنماط عربية
    for kw in AR_VIDEO_KEYWORDS:
        if kw in text:
            after = text.split(kw, 1)[-1].strip(" :،,.!-؟")
            return after or text

    # أنماط إنجليزية
    for kw in EN_VIDEO_KEYWORDS:
        if kw in lower:
            after = lower.split(kw, 1)[-1].strip(" :,.!-?")
            return after or text

    return None


def detect_message_language(text: str, requested_lang: Optional[str] = None) -> str:
    """
    Detect language based on content; prioritize Arabic characters, else English.
    Even if user requested a different language, we respond in the message language.
    """
    txt = text or ""
    has_ar = any("\u0600" <= ch <= "\u06FF" for ch in txt)
    if has_ar:
        return "ar"
    # fallback to requested if provided, else default to en
    return requested_lang or "en"


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


class ConversationsQuery(BaseModel):
    user_id: Optional[str] = None
    limit: Optional[int] = 20


app = FastAPI(title="Chatbot FastAPI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "ok",
        "chatbot_loaded": CHATBOT_LOADED,
        "database_available": DB_AVAILABLE,
        "web_search_available": web_search is not None,
        "react_build_exists": REACT_BUILD_EXISTS,
        "timestamp": datetime.now().isoformat()
    }


# ==================== Authentication Endpoints ====================

@app.post("/api/auth/register")
async def register_endpoint(payload: RegisterRequest):
    """تسجيل مستخدم جديد"""
    try:
        from auth import create_user
        
        result = create_user(
            username=payload.username,
            password=payload.password,
            email=payload.email,
            full_name=payload.full_name
        )
        
        if result.get("success"):
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "فشل التسجيل"))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in register: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="خطأ في التسجيل")


@app.post("/api/auth/login")
async def login_endpoint(payload: LoginRequest):
    """تسجيل الدخول"""
    try:
        from auth import authenticate_user
        
        result = authenticate_user(
            username=payload.username,
            password=payload.password
        )
        
        if result.get("success"):
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=401, detail=result.get("error", "فشل تسجيل الدخول"))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in login: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="خطأ في تسجيل الدخول")


@app.get("/api/auth/user/{username}")
async def get_user_endpoint(username: str):
    """الحصول على بيانات المستخدم"""
    try:
        from auth import get_user_by_username
        
        user = get_user_by_username(username)
        
        if user:
            return JSONResponse({"success": True, "user": user})
        else:
            raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error getting user: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="خطأ في جلب بيانات المستخدم")


@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    message = (payload.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Get user info if logged in
    user_id = payload.user_id or "anonymous"
    user_name = None
    
    # Try to get user name from username if provided
    if user_id and user_id != "anonymous":
        try:
            from auth import get_user_by_username
            user_data = get_user_by_username(user_id)
            if user_data:
                user_name = user_data.get("full_name") or user_data.get("username")
                user_id = str(user_data.get("id", user_id))
        except Exception as e:
            logger.debug(f"Could not get user info: {e}")
    
    # Force response language to follow the message content, not UI toggle
    language = detect_message_language(message, payload.language)
    conversation_mode = payload.conversation_mode or "smart"

    # Live web search to enrich context + store for training
    web_results: List[Dict[str, Any]] = []
    try:
        web_results = web_search.search_and_scrape(message, max_results=3)
    except Exception as exc:  # pragma: no cover - best-effort search
        logger.warning(f"Web search failed: {exc}")

    try:
        result = chatbot.process_message(
            message=message,
            user_id=user_id,
            lang=language,
            image_data=None,
        )
    except Exception as exc:
        logger.error(f"Error processing message: {exc}", exc_info=True)
        detail = "عذراً، حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى." if language == "ar" else "Sorry, an error occurred while processing your message."
        raise HTTPException(status_code=500, detail=detail)

    # إذا لم نجد مصادر أو رد مناسب، أعطِ إجابة افتراضية توضح ذلك
    if (not result.get("response")) and (not web_results):
        fallback_ar = "لم أجد معلومات موثوقة حالياً، هل يمكنك توضيح السؤال أو تزويدي بتفاصيل أكثر؟"
        fallback_en = "I could not find reliable info right now. Could you clarify or give more details?"
        result["response"] = fallback_ar if (language == "ar" or "ar" in (result.get("detected_lang") or "")) else fallback_en

    # Persist conversation + training sample with quality improvement
    training_saved = False
    improved_response = result.get("response", "")
    
    if DB_AVAILABLE:
        try:
            # استخدام نظام تحسين الجودة
            from response_quality_improver import get_response_improver
            response_improver = get_response_improver()
            
            # معالجة وتحسين الرد
            improvement_result = response_improver.process_and_save(
                user_id=user_id,
                message=message,
                response=result.get("response", ""),
                search_results=web_results,
                intent=result.get("intent", "general"),
                sentiment=result.get("sentiment", "neutral"),
                confidence=result.get("confidence", 0.8),
            )
            
            # استخدام الرد المحسّن إذا كان أفضل
            if improvement_result.get('was_improved') and improvement_result.get('improved_response'):
                improved_response = improvement_result['improved_response']
                logger.info(f"✅ Response improved (quality score: {improvement_result.get('quality_analysis', {}).get('quality_score', 0):.2f})")
            
            # حفظ المحادثة
            save_conversation(
                user_id=user_id,
                message=message,
                response=improved_response,
                intent=result.get("intent", "general"),
                sentiment=result.get("sentiment", "neutral"),
                confidence=result.get("confidence", 0.8),
            )
            
            training_saved = improvement_result.get('saved_as_training', False)
            
        except Exception as exc:  # pragma: no cover - DB optional
            logger.warning(f"Failed to save training data: {exc}")
            # Fallback: حفظ عادي بدون تحسين
            try:
                save_conversation(
                    user_id=user_id,
                    message=message,
                    response=result.get("response", ""),
                    intent=result.get("intent", "general"),
                    sentiment=result.get("sentiment", "neutral"),
                    confidence=result.get("confidence", 0.8),
                )
                save_training_sample(
                    user_id=user_id,
                    message=message,
                    response=result.get("response", ""),
                    search_results=web_results,
                    tags=[conversation_mode] if conversation_mode else None,
                    intent=result.get("intent", "general"),
                    sentiment=result.get("sentiment", "neutral"),
                    confidence=result.get("confidence", 0.8),
                )
                training_saved = True
            except:
                pass

    # Format response nicely with beautiful formatting
    response_text = improved_response or result.get("response", "")  # استخدام الرد المحسّن أو الافتراضي
    
    # Add user name to response if available
    if user_name:
        greeting = f"مرحباً {user_name}! " if language == "ar" else f"Hello {user_name}! "
        # Only add greeting if response doesn't already contain user name
        if user_name.lower() not in response_text.lower():
            response_text = greeting + response_text
    
    # Detect language for better formatting
    detected_lang = result.get("detected_lang", "en")
    is_arabic = detected_lang == "ar" or any('\u0600' <= char <= '\u06FF' for char in message)
    
    # Enhance response with simple, clean web results (titles + links فقط)
    if web_results and len(web_results) > 0:
        lines: List[str] = []
        if is_arabic:
            lines.append("")
            lines.append("📚 مصادر مفيدة من الإنترنت (مختصرة):")
        else:
            lines.append("")
            lines.append("📚 Helpful web sources (short list):")

        for idx, res in enumerate(web_results[:3], 1):
            title = res.get("title") or ( "بدون عنوان" if is_arabic else "No title" )
            url = res.get("url", "")
            # ما نستخدمش النص الخام الطويل؛ بس نعرض العنوان والرابط
            if url:
                lines.append(f"{idx}. {title} → {url}")
            else:
                lines.append(f"{idx}. {title}")

        response_text += "\n" + "\n".join(lines)
    
    # Optional: YouTube video suggestion when user asks for a video explanation
    youtube_video: Optional[YoutubeVideo] = None
    try:
        video_query = extract_video_query(message)
        if video_query:
            youtube_video = await search_youtube_video(video_query)
    except Exception as exc:
        logger.warning(f"YouTube search failed: {exc}")

    # Create beautiful formatted response
    formatted_response = {
        "success": True,
        "response": response_text,
        "detected_lang": detected_lang,
        "intent": result.get("intent", "general"),
        "sentiment": result.get("sentiment", "neutral"),
        "source": result.get("source", "ai"),
        "web_results": web_results,
        "web_results_count": len(web_results),
        "training_saved": training_saved,
        "chatbot_loaded": CHATBOT_LOADED,
        "timestamp": datetime.now().isoformat(),
        "message_preview": message[:50] + "..." if len(message) > 50 else message,
        "user_name": user_name,  # Add user name to response
        "user_id": user_id,
    }

    if youtube_video is not None:
        # Keep snake_case keys to stay consistent with existing API style
        formatted_response["youtube_video"] = youtube_video.dict()
    
    return JSONResponse(formatted_response)


@app.post("/api/chat/stream")
async def chat_stream_endpoint(payload: ChatRequest):
    """Streaming endpoint for real-time responses"""
    message = (payload.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    user_id = payload.user_id or "anonymous"
    # Force response language to follow the message content, not UI toggle
    language = detect_message_language(message, payload.language)
    conversation_mode = payload.conversation_mode or "smart"

    async def generate_stream():
        try:
            if not chatbot:
                yield f"data: {json.dumps({'error': 'Chatbot service is not available', 'done': True})}\n\n"
                return
            
            # Process message
            result = chatbot.process_message(
                message=message,
                user_id=user_id,
                lang=language,
                image_data=None,
            )
            
            response_text = result.get("response", "")
            
            # Stream response word by word
            words = response_text.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                await asyncio.sleep(0.05)  # Small delay for smooth streaming
            
            # Send completion
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
        except Exception as exc:
            logger.error(f"Streaming error: {exc}", exc_info=True)
            yield f"data: {json.dumps({'error': str(exc), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/search")
async def search_endpoint(payload: SearchRequest):
    query = (payload.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        results = web_search.search_and_scrape(query, max_results=payload.max_results or 5)
    except Exception as exc:  # pragma: no cover
        logger.error(f"Search error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed") from exc

    return {"success": True, "count": len(results), "results": results}


@app.get("/api/conversations")
async def conversations_endpoint(user_id: Optional[str] = None, limit: int = 20):
    try:
        data = get_conversations(user_id=user_id, limit=limit)
        return {"success": True, "count": len(data), "conversations": data}
    except Exception as exc:  # pragma: no cover
        logger.error(f"Error fetching conversations: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")


@app.get("/api/training")
async def training_endpoint(user_id: Optional[str] = None, limit: int = 20):
    try:
        data = get_training_samples(user_id=user_id, limit=limit)
        return {"success": True, "count": len(data), "samples": data}
    except Exception as exc:  # pragma: no cover
        logger.error(f"Error fetching training samples: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch training samples")

@app.get("/api/training/quality")
async def get_training_quality_endpoint(user_id: Optional[str] = None):
    """Get training data quality analysis"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from training_enhancer import get_training_enhancer
        enhancer = get_training_enhancer()
        analysis = enhancer.analyze_training_data(user_id=user_id)
        return JSONResponse({"success": True, "analysis": analysis})
    except Exception as exc:
        logger.error(f"Error analyzing training quality: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/training/high-quality")
async def get_high_quality_samples_endpoint(user_id: Optional[str] = None, limit: int = 100):
    """Get high quality training samples"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from training_enhancer import get_training_enhancer
        enhancer = get_training_enhancer()
        samples = enhancer.get_high_quality_samples(user_id=user_id, limit=limit)
        return JSONResponse({"success": True, "samples": samples, "count": len(samples)})
    except Exception as exc:
        logger.error(f"Error getting high quality samples: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/training/export")
async def export_training_data_endpoint(
    format: str = "openai",
    user_id: Optional[str] = None,
    limit: int = 1000
):
    """Export training data in different formats"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from training_data_exporter import get_training_exporter
        exporter = get_training_exporter()
        
        if format == "openai":
            count = exporter.export_for_openai_finetuning(
                output_file=f"openai_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                user_id=user_id,
                limit=limit
            )
            return JSONResponse({
                "success": True,
                "format": "openai",
                "count": count,
                "message": f"Exported {count} samples for OpenAI fine-tuning"
            })
        elif format == "chatgpt":
            count = exporter.export_for_chatgpt_training(
                output_file=f"chatgpt_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                user_id=user_id,
                limit=limit
            )
            return JSONResponse({
                "success": True,
                "format": "chatgpt",
                "count": count,
                "message": f"Exported {count} samples for ChatGPT training"
            })
        else:
            raise HTTPException(status_code=400, detail=f"Unknown format: {format}")
    except Exception as exc:
        logger.error(f"Error exporting training data: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/training/statistics")
async def get_training_statistics_endpoint(user_id: Optional[str] = None):
    """Get training data statistics"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from training_data_exporter import get_training_exporter
        exporter = get_training_exporter()
        stats = exporter.export_statistics(
            output_file=f"training_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            user_id=user_id
        )
        return JSONResponse({"success": True, "statistics": stats})
    except Exception as exc:
        logger.error(f"Error getting training statistics: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ==================== Links Endpoints ====================

@app.get("/api/links")
async def get_links_endpoint(source: Optional[str] = None, limit: int = 50):
    """الحصول على قائمة الروابط المحفوظة"""
    try:
        from database import get_scraped_data
        if source:
            links = get_scraped_data(source=source, limit=limit)
        else:
            links = get_scraped_data(limit=limit)
        return {"success": True, "count": len(links), "links": links}
    except Exception as exc:
        logger.error(f"Error getting links: {exc}", exc_info=True)
        return {"success": False, "error": str(exc), "links": []}


@app.post("/api/links")
async def add_link_endpoint(
    payload: Optional[Dict[str, Any]] = Body(None),
    url: Optional[str] = Query(None)
):
    """إضافة رابط جديد لاستخراج البيانات منه"""
    try:
        # دعم أكثر من طريقة لإرسال الرابط:
        # 1) JSON body: {"url": "https://example.com"}
        # 2) Query param: /api/links?url=...
        raw_url = url
        if (not raw_url) and payload:
            raw_url = payload.get("url")

        final_url = (raw_url or "").strip()

        if not final_url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        if not final_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Try to scrape immediately
        try:
            from database import save_scraped_data
            scraper = core.get_web_scraper() if core else None
            if scraper:
                result = scraper.scrape_url(final_url, force_refresh=False)
                if result.get("success"):
                    save_scraped_data(
                        url=final_url,
                        title=result.get("title", ""),
                        description=result.get("description", ""),
                        content=result.get("content", ""),
                        source=result.get("source", "general"),
                        metadata=result.get("webteb_data") or result.get("wikipedia_data") or {}
                    )
                    return JSONResponse({
                        "success": True,
                        "message": "تم إضافة الرابط واستخراج البيانات بنجاح",
                        "url": final_url,
                        "data": {
                            "title": result.get("title"),
                            "description": result.get("description", "")[:200],
                            "content_length": len(result.get("content", ""))
                        }
                    })
        except Exception as scrape_error:
            logger.warning(f"Immediate scrape failed: {scrape_error}")
        
        # Add to queue if available
        try:
            manager = core.get_scraper_manager() if core else None
            if manager:
                manager.add_url(final_url, priority=5, force_refresh=False)
            return JSONResponse({
                "success": True,
                "message": "تم إضافة الرابط للقائمة، سيتم معالجته قريباً",
                "url": final_url
            })
        except Exception as queue_error:
            logger.warning(f"Failed to add to queue: {queue_error}")
            return JSONResponse({
                "success": True,
                "message": "تم استلام الرابط، سيتم معالجته لاحقاً",
                "url": final_url
            })
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error adding link: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ==================== Voice Processing Endpoints ====================

from fastapi import File, UploadFile, Form
import io

@app.post("/api/voice/speech-to-text")
async def speech_to_text_endpoint(
    audio: Optional[UploadFile] = File(None),
    language: Optional[str] = Form("en")
):
    """تحويل الكلام إلى نص - Speech to Text"""
    try:
        # Handle case where audio might not be provided
        if audio is None:
            # Try to get from request body as fallback
            try:
                from fastapi import Request
                request: Request = Request
                if request.headers.get("content-type", "").startswith("multipart/form-data"):
                    raise HTTPException(status_code=400, detail="No audio file provided")
            except:
                pass
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Read audio data
        audio_data = await audio.read()
        
        if not audio_data or len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Validate audio file size (max 10MB)
        if len(audio_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 10MB)")
        
        # Try to use voice processor
        try:
            from voice_processing import VoiceProcessor
            processor = VoiceProcessor()
            result = processor.speech_to_text(audio_data, language or "en")
            
            if result.get("success"):
                return JSONResponse({
                    "success": True,
                    "text": result.get("text", ""),
                    "confidence": result.get("confidence", 0.8),
                    "language": result.get("language", language or "en")
                })
            else:
                return JSONResponse({
                    "success": False,
                    "error": result.get("error", "Speech recognition failed"),
                    "text": ""
                }, status_code=400)
        except ImportError:
            logger.warning("voice_processing module not available, using browser fallback")
            # Fallback: suggest using browser API
            return JSONResponse({
                "success": False,
                "error": "Voice processing not available. Please use browser speech recognition API.",
                "text": "",
                "suggestion": "Use Web Speech API in browser"
            }, status_code=503)
        except Exception as proc_error:
            logger.error(f"Voice processing error: {proc_error}", exc_info=True)
            return JSONResponse({
                "success": False,
                "error": f"Voice processing failed: {str(proc_error)}",
                "text": ""
            }, status_code=500)
            
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error in speech-to-text: {exc}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(exc),
            "text": ""
        }, status_code=500)


@app.post("/api/voice/text-to-speech")
async def text_to_speech_endpoint(payload: Dict[str, Any]):
    """تحويل النص إلى كلام - Text to Speech"""
    try:
        text = (payload.get("text") or "").strip()
        language = payload.get("language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Try to use voice processor
        try:
            from voice_processing import VoiceProcessor
            processor = VoiceProcessor()
            result = processor.text_to_speech(text, language)
            
            if result.get("success") and result.get("filepath"):
                # Return audio file
                def generate():
                    with open(result["filepath"], "rb") as f:
                        yield from f
                
                return StreamingResponse(
                    generate(),
                    media_type="audio/wav",
                    headers={"Content-Disposition": "attachment; filename=speech.wav"}
                )
            else:
                return JSONResponse({
                    "success": False,
                    "error": result.get("error", "Text-to-speech failed")
                }, status_code=500)
        except ImportError:
            logger.warning("voice_processing module not available")
            return JSONResponse({
                "success": False,
                "error": "Voice processing not available. Please install pyttsx3."
            }, status_code=503)
            
    except Exception as exc:
        logger.error(f"Error in text-to-speech: {exc}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(exc)
        }, status_code=500)


# ==================== Upload Endpoints ====================

@app.post("/api/upload/image")
async def upload_image_endpoint(file: UploadFile = File(...)):
    """رفع ومعالجة صورة"""
    try:
        image_data = await file.read()
        
        if not image_data:
            raise HTTPException(status_code=400, detail="No file provided")
        
        import base64
        import os
        from datetime import datetime
        
        # Create uploads directory
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(upload_dir, safe_filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # Get image info
        try:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            format_name = image.format or "UNKNOWN"
        except:
            width, height = 0, 0
            format_name = "UNKNOWN"
        
        return JSONResponse({
            "success": True,
            "data": {
                "type": "image",
                "format": format_name,
                "width": width,
                "height": height,
                "size_bytes": len(image_data),
                "base64": image_base64,
                "filepath": filepath,
                "filename": safe_filename
            }
        })
        
    except Exception as exc:
        logger.error(f"Error uploading image: {exc}", exc_info=True)
        return JSONResponse({
            "success": False,
            "error": str(exc)
        }, status_code=500)


# Serve React build if present (mounted after API routes to avoid swallowing /api/*)
if REACT_BUILD_EXISTS:
    app.mount("/", StaticFiles(directory=REACT_BUILD_DIR, html=True), name="static")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        return FileResponse(os.path.join(REACT_BUILD_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)

