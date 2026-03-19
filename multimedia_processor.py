# multimedia_processor.py: معالجة الوسائط المتعددة (صور، صوت، فيديو)
import logging
import base64
import io
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import os

logger = logging.getLogger(__name__)

class MultimediaProcessor:
    """معالج الوسائط المتعددة للشاتبوت"""
    
    # الصيغ المدعومة
    SUPPORTED_IMAGE_FORMATS = ['JPEG', 'PNG', 'GIF', 'WebP', 'BMP']
    SUPPORTED_AUDIO_FORMATS = ['MP3', 'WAV', 'OGG', 'M4A', 'FLAC']
    SUPPORTED_VIDEO_FORMATS = ['MP4', 'AVI', 'MOV', 'WEBM']
    
    # حدود الحجم (بالبايت)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(self):
        self.upload_dir = 'uploads'
        os.makedirs(self.upload_dir, exist_ok=True)
        logger.info("MultimediaProcessor initialized")
    
    def process_image(self, image_data: bytes, filename: str = None) -> Dict[str, Any]:
        """معالجة الصورة"""
        try:
            # فحص الحجم
            if len(image_data) > self.MAX_IMAGE_SIZE:
                return {
                    'success': False,
                    'error': f'Image size exceeds {self.MAX_IMAGE_SIZE / 1024 / 1024}MB limit'
                }
            
            # فتح الصورة
            image = Image.open(io.BytesIO(image_data))
            
            # معلومات الصورة
            width, height = image.size
            format_name = image.format or 'UNKNOWN'
            mode = image.mode
            
            # حساب Color Depth
            color_depth = self._get_color_depth(mode)
            
            # التحويل إلى Base64 للرسائل
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # حفظ الصورة
            if filename:
                filepath = os.path.join(self.upload_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
            else:
                filepath = None
            
            return {
                'success': True,
                'type': 'image',
                'format': format_name,
                'width': width,
                'height': height,
                'mode': mode,
                'color_depth': color_depth,
                'size_bytes': len(image_data),
                'base64': image_base64,
                'filepath': filepath
            }
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_audio(self, audio_data: bytes, filename: str = None) -> Dict[str, Any]:
        """معالجة الصوت"""
        try:
            # فحص الحجم
            if len(audio_data) > self.MAX_AUDIO_SIZE:
                return {
                    'success': False,
                    'error': f'Audio size exceeds {self.MAX_AUDIO_SIZE / 1024 / 1024}MB limit'
                }
            
            # حفظ الملف
            if filename:
                filepath = os.path.join(self.upload_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(audio_data)
            else:
                filepath = None
            
            return {
                'success': True,
                'type': 'audio',
                'size_bytes': len(audio_data),
                'filepath': filepath
            }
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_video(self, video_data: bytes, filename: str = None) -> Dict[str, Any]:
        """معالجة الفيديو"""
        try:
            # فحص الحجم
            if len(video_data) > self.MAX_VIDEO_SIZE:
                return {
                    'success': False,
                    'error': f'Video size exceeds {self.MAX_VIDEO_SIZE / 1024 / 1024}MB limit'
                }
            
            # حفظ الملف
            if filename:
                filepath = os.path.join(self.upload_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(video_data)
            else:
                filepath = None
            
            return {
                'success': True,
                'type': 'video',
                'size_bytes': len(video_data),
                'filepath': filepath
            }
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_color_depth(self, mode: str) -> int:
        """حساب Color Depth من mode"""
        depth_map = {
            '1': 1,      # 1-bit (أبيض وأسود)
            'L': 8,      # 8-bit grayscale
            'P': 8,      # 8-bit palette (GIF)
            'RGB': 24,   # 24-bit True Color
            'RGBA': 32,  # 32-bit (24-bit + 8-bit Alpha)
            'CMYK': 32,  # 32-bit
            'LAB': 24,   # 24-bit
        }
        return depth_map.get(mode, 24)
    
    def validate_file_type(self, filename: str, file_type: str) -> bool:
        """التحقق من نوع الملف"""
        extension = filename.split('.')[-1].upper()
        
        if file_type == 'image':
            return extension in [f.replace('WebP', 'WEBP') for f in self.SUPPORTED_IMAGE_FORMATS]
        elif file_type == 'audio':
            return extension in self.SUPPORTED_AUDIO_FORMATS
        elif file_type == 'video':
            return extension in self.SUPPORTED_VIDEO_FORMATS
        
        return False

# Singleton instance
_multimedia_processor = None

def get_multimedia_processor() -> MultimediaProcessor:
    """الحصول على instance واحد من MultimediaProcessor"""
    global _multimedia_processor
    if _multimedia_processor is None:
        _multimedia_processor = MultimediaProcessor()
    return _multimedia_processor

