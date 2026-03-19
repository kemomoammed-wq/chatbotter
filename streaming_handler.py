# streaming_handler.py: معالجة Streaming للردود
import logging
import json
from typing import Generator, Dict, Any, Optional
from flask import Response, stream_with_context

logger = logging.getLogger(__name__)

class StreamingHandler:
    """معالج Streaming للردود"""
    
    def __init__(self):
        logger.info("StreamingHandler initialized")
    
    def stream_response(self, text: str, chunk_size: int = 10) -> Generator[str, None, None]:
        """تحويل النص إلى chunks للـ streaming"""
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_with_space = word + ' '
            word_length = len(word_with_space)
            
            if current_length + word_length > chunk_size and current_chunk:
                # إرسال الـ chunk الحالي
                chunk_text = ''.join(current_chunk)
                yield f"data: {json.dumps({'chunk': chunk_text, 'done': False})}\n\n"
                current_chunk = [word_with_space]
                current_length = word_length
            else:
                current_chunk.append(word_with_space)
                current_length += word_length
        
        # إرسال آخر chunk
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            yield f"data: {json.dumps({'chunk': chunk_text, 'done': False})}\n\n"
        
        # إرسال إشارة الانتهاء
        yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
    
    def create_streaming_response(self, text: str) -> Response:
        """إنشاء Response للـ streaming"""
        return Response(
            stream_with_context(self.stream_response(text)),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    
    def stream_llm_response(self, llm_generator) -> Generator[str, None, None]:
        """Streaming من LLM generator مباشرة"""
        try:
            for chunk in llm_generator:
                if isinstance(chunk, dict):
                    chunk_text = chunk.get('text', '') or chunk.get('content', '')
                else:
                    chunk_text = str(chunk)
                
                if chunk_text:
                    yield f"data: {json.dumps({'chunk': chunk_text, 'done': False})}\n\n"
            
            # إرسال إشارة الانتهاء
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            error_msg = json.dumps({'error': str(e), 'done': True})
            yield f"data: {error_msg}\n\n"

# Singleton instance
_streaming_handler = None

def get_streaming_handler() -> StreamingHandler:
    """الحصول على instance واحد من StreamingHandler"""
    global _streaming_handler
    if _streaming_handler is None:
        _streaming_handler = StreamingHandler()
    return _streaming_handler

