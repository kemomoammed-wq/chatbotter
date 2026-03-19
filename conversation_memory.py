# conversation_memory.py: Advanced Conversation Memory Management (ChatGPT-like)
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque
import pickle
import os

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Advanced conversation memory with context management"""
    
    def __init__(self, max_history: int = 20, max_context_length: int = 4000):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of messages to keep in memory
            max_context_length: Maximum tokens/characters for context window
        """
        self.max_history = max_history
        self.max_context_length = max_context_length
        self.conversations: Dict[str, deque] = {}  # user_id -> message history
        self.user_profiles: Dict[str, Dict] = {}   # user_id -> user profile
        self.context_summaries: Dict[str, str] = {} # user_id -> context summary
        
    def add_message(self, user_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = deque(maxlen=self.max_history)
        
        message = {
            'role': role,  # 'user', 'assistant', 'system'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversations[user_id].append(message)
        
        # Auto-summarize if context gets too long
        if self._get_context_length(user_id) > self.max_context_length:
            self._summarize_context(user_id)
    
    def get_messages(self, user_id: str, include_system: bool = True, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation messages for a user"""
        if user_id not in self.conversations:
            return []
        
        messages = list(self.conversations[user_id])
        
        # Filter system messages if needed
        if not include_system:
            messages = [msg for msg in messages if msg['role'] != 'system']
        
        # Apply limit
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_formatted_messages(self, user_id: str, system_prompt: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get messages formatted for LLM API"""
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Get conversation messages
        conv_messages = self.get_messages(user_id, include_system=False, limit=limit)
        messages.extend(conv_messages)
        
        return messages
    
    def clear_conversation(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            self.conversations[user_id].clear()
        if user_id in self.context_summaries:
            del self.context_summaries[user_id]
    
    def get_context_summary(self, user_id: str) -> str:
        """Get summary of conversation context"""
        if user_id in self.context_summaries:
            return self.context_summaries[user_id]
        
        if user_id not in self.conversations or len(self.conversations[user_id]) == 0:
            return "No previous conversation."
        
        # Create simple summary
        messages = list(self.conversations[user_id])
        summary_parts = []
        
        # Extract key topics
        topics = set()
        for msg in messages:
            if msg['role'] == 'user':
                content = msg['content'][:50]  # First 50 chars
                topics.add(content)
        
        summary = f"Previous conversation: {len(messages)} messages. Topics discussed: {', '.join(list(topics)[:5])}"
        
        self.context_summaries[user_id] = summary
        return summary
    
    def _get_context_length(self, user_id: str) -> int:
        """Calculate total context length"""
        if user_id not in self.conversations:
            return 0
        
        total = 0
        for msg in self.conversations[user_id]:
            total += len(msg.get('content', ''))
        return total
    
    def _summarize_context(self, user_id: str):
        """Summarize old messages to save space"""
        if user_id not in self.conversations:
            return
        
        messages = list(self.conversations[user_id])
        if len(messages) < 3:
            return
        
        # Keep recent messages, summarize old ones
        recent = messages[-5:]  # Keep last 5 messages
        old = messages[:-5]     # Summarize older messages
        
        # Create summary of old messages
        old_summary = f"Previous conversation summary: {len(old)} messages about various topics."
        
        # Clear and rebuild with summary
        self.conversations[user_id].clear()
        
        # Add summary as system message
        summary_message = {
            'role': 'system',
            'content': old_summary,
            'timestamp': datetime.now().isoformat(),
            'metadata': {'summarized': True}
        }
        self.conversations[user_id].append(summary_message)
        
        # Add recent messages
        for msg in recent:
            self.conversations[user_id].append(msg)
    
    def update_user_profile(self, user_id: str, profile_data: Dict):
        """Update user profile information"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        
        self.user_profiles[user_id].update(profile_data)
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile"""
        return self.user_profiles.get(user_id, {})
    
    def save_to_file(self, filepath: str):
        """Save conversations to file"""
        try:
            data = {
                'conversations': {
                    user_id: list(messages) 
                    for user_id, messages in self.conversations.items()
                },
                'user_profiles': self.user_profiles,
                'context_summaries': self.context_summaries
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Conversations saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving conversations: {e}")
    
    def load_from_file(self, filepath: str):
        """Load conversations from file"""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Conversation file not found: {filepath}")
                return
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.conversations = {
                user_id: deque(messages, maxlen=self.max_history)
                for user_id, messages in data.get('conversations', {}).items()
            }
            self.user_profiles = data.get('user_profiles', {})
            self.context_summaries = data.get('context_summaries', {})
            
            logger.info(f"Conversations loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")

# Global instance
_memory = None

def get_conversation_memory() -> ConversationMemory:
    """Get global conversation memory instance"""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
        # Try to load from file
        _memory.load_from_file('logs/conversations.pkl')
    return _memory

