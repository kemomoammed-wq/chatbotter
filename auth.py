"""
نظام المصادقة - Authentication System
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import Session, User
import logging

logger = logging.getLogger(__name__)

# JWT-like token system (simplified)
SECRET_KEY = secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """التحقق من كلمة المرور"""
    return hash_password(password) == password_hash

def create_user(username: str, password: str, email: Optional[str] = None, full_name: Optional[str] = None) -> Dict[str, Any]:
    """إنشاء مستخدم جديد"""
    try:
        session = Session()
        
        # التحقق من وجود المستخدم
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return {
                "success": False,
                "error": "اسم المستخدم أو البريد الإلكتروني موجود بالفعل"
            }
        
        # إنشاء مستخدم جديد
        password_hash = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name or username,
            language='ar',
            created_at=datetime.utcnow(),
            is_active=1
        )
        
        session.add(new_user)
        session.commit()
        
        user_data = {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "language": new_user.language,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
        }
        
        logger.info(f"✅ User created: {username}")
        return {
            "success": True,
            "user": user_data,
            "message": "تم إنشاء الحساب بنجاح"
        }
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}", exc_info=True)
        session.rollback()
        return {
            "success": False,
            "error": f"خطأ في إنشاء الحساب: {str(e)}"
        }
    finally:
        session.close()

def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """المصادقة وتسجيل الدخول"""
    try:
        session = Session()
        
        # البحث عن المستخدم
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            return {
                "success": False,
                "error": "اسم المستخدم أو كلمة المرور غير صحيحة"
            }
        
        # التحقق من كلمة المرور
        if not verify_password(password, user.password_hash):
            return {
                "success": False,
                "error": "اسم المستخدم أو كلمة المرور غير صحيحة"
            }
        
        # التحقق من أن الحساب نشط
        if not user.is_active:
            return {
                "success": False,
                "error": "الحساب غير نشط"
            }
        
        # تحديث آخر تسجيل دخول
        user.last_login = datetime.utcnow()
        session.commit()
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "language": user.language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        logger.info(f"✅ User logged in: {username}")
        return {
            "success": True,
            "user": user_data,
            "message": "تم تسجيل الدخول بنجاح"
        }
    except Exception as e:
        logger.error(f"❌ Error authenticating user: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"خطأ في تسجيل الدخول: {str(e)}"
        }
    finally:
        session.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """الحصول على بيانات المستخدم"""
    try:
        session = Session()
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "language": user.language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}", exc_info=True)
        return None
    finally:
        session.close()

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """الحصول على بيانات المستخدم بالاسم"""
    try:
        session = Session()
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "language": user.language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}", exc_info=True)
        return None
    finally:
        session.close()

