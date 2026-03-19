# memory_manager.py: إدارة الذاكرة والمحادثات
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sqlite3
import os

logger = logging.getLogger(__name__)

class MemoryManager:
    """مدير الذاكرة للمحادثات"""
    
    def __init__(self, db_path: str = 'logs/chatbot.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
        logger.info("MemoryManager initialized")
    
    def _init_database(self):
        """تهيئة قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول المحادثات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversation_sessions(id)
                )
            ''')
            
            # جدول جلسات المحادثة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الذاكرة طويلة المدى
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, key)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def save_conversation(self, user_id: str, conversation_id: str, 
                         message: str, response: str, metadata: Dict = None):
        """حفظ محادثة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
                INSERT INTO conversations (user_id, conversation_id, message, response, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, conversation_id, message, response, metadata_json))
            
            # تحديث updated_at للجلسة
            cursor.execute('''
                UPDATE conversation_sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (conversation_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """الحصول على تاريخ المحادثة"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT message, response, timestamp, metadata
                FROM conversations
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (conversation_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'message': row['message'],
                    'response': row['response'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            return list(reversed(history))  # ترتيب من الأقدم للأحدث
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def create_conversation_session(self, user_id: str, title: str = None) -> str:
        """إنشاء جلسة محادثة جديدة"""
        try:
            import uuid
            conversation_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_sessions (id, user_id, title)
                VALUES (?, ?, ?)
            ''', (conversation_id, user_id, title))
            
            conn.commit()
            conn.close()
            
            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation session: {e}")
            return None
    
    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Dict]:
        """الحصول على محادثات المستخدم"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, created_at, updated_at,
                       (SELECT COUNT(*) FROM conversations WHERE conversation_id = conversation_sessions.id) as message_count
                FROM conversation_sessions
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in rows:
                conversations.append({
                    'id': row['id'],
                    'title': row['title'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'message_count': row['message_count']
                })
            
            return conversations
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    def save_memory(self, user_id: str, key: str, value: str, importance: float = 0.5):
        """حفظ ذاكرة طويلة المدى"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO long_term_memory (user_id, key, value, importance, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, key, value, importance))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def get_memory(self, user_id: str, key: str = None) -> List[Dict]:
        """الحصول على الذاكرة"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if key:
                cursor.execute('''
                    SELECT key, value, importance, updated_at
                    FROM long_term_memory
                    WHERE user_id = ? AND key = ?
                ''', (user_id, key))
            else:
                cursor.execute('''
                    SELECT key, value, importance, updated_at
                    FROM long_term_memory
                    WHERE user_id = ?
                    ORDER BY importance DESC, updated_at DESC
                ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            memories = []
            for row in rows:
                memories.append({
                    'key': row['key'],
                    'value': row['value'],
                    'importance': row['importance'],
                    'updated_at': row['updated_at']
                })
            
            return memories
        except Exception as e:
            logger.error(f"Error getting memory: {e}")
            return []
    
    def summarize_conversation(self, conversation_id: str, max_length: int = 2000) -> str:
        """تلخيص محادثة طويلة"""
        history = self.get_conversation_history(conversation_id, limit=100)
        
        if len(history) < 5:
            return ""
        
        # بناء ملخص بسيط
        summary_parts = []
        for i, item in enumerate(history[:10]):  # أول 10 رسائل
            summary_parts.append(f"User: {item['message'][:100]}")
            summary_parts.append(f"Bot: {item['response'][:100]}")
        
        summary = "\n".join(summary_parts)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary

# Singleton instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """الحصول على instance واحد من MemoryManager"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

