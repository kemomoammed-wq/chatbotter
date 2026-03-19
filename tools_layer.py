# tools_layer.py: طبقة الأدوات (كود، بحث، ملفات)
import logging
import subprocess
import json
import os
from typing import Dict, Any, Optional, List
import tempfile

logger = logging.getLogger(__name__)

class ToolsLayer:
    """طبقة الأدوات للشاتبوت"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info("ToolsLayer initialized")
    
    def execute_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """تنفيذ كود"""
        try:
            if language.lower() != 'python':
                return {
                    'success': False,
                    'error': f'Language {language} not supported yet'
                }
            
            # إنشاء ملف مؤقت
            temp_file = os.path.join(self.temp_dir, f'temp_code_{os.getpid()}.py')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # تنفيذ الكود في sandbox
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.temp_dir
            )
            
            # حذف الملف المؤقت
            try:
                os.remove(temp_file)
            except:
                pass
            
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Code execution timeout (10 seconds)'
            }
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """البحث على الويب"""
        try:
            # استخدام web_search_service الموجود
            from web_search_service import get_web_search_service
            
            search_service = get_web_search_service()
            results = search_service.search(query, max_results=max_results)
            
            return {
                'success': True,
                'results': results
            }
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def analyze_file(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """تحليل ملف"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            file_size = os.path.getsize(file_path)
            
            # تحديد نوع الملف
            if not file_type:
                extension = file_path.split('.')[-1].lower()
                file_type = extension
            
            result = {
                'success': True,
                'file_path': file_path,
                'file_type': file_type,
                'file_size': file_size,
                'content': None
            }
            
            # قراءة المحتوى حسب النوع
            if file_type in ['txt', 'md', 'py', 'js', 'ts', 'json', 'xml', 'html', 'css']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        result['content'] = content[:10000]  # أول 10000 حرف
                except:
                    result['content'] = None
            
            elif file_type == 'pdf':
                # يحتاج مكتبة pdf
                result['content'] = 'PDF file - requires PDF parser'
            
            elif file_type in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                result['content'] = 'Image file'
            
            elif file_type in ['mp3', 'wav', 'ogg', 'm4a']:
                result['content'] = 'Audio file'
            
            elif file_type in ['mp4', 'avi', 'mov', 'webm']:
                result['content'] = 'Video file'
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """حساب تعبير رياضي"""
        try:
            # استخدام eval بشكل آمن
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return {
                    'success': False,
                    'error': 'Invalid characters in expression'
                }
            
            result = eval(expression)
            
            return {
                'success': True,
                'expression': expression,
                'result': result
            }
        except Exception as e:
            logger.error(f"Error calculating: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_tools(self) -> List[str]:
        """الحصول على قائمة الأدوات المتاحة"""
        return [
            'execute_code',
            'search_web',
            'analyze_file',
            'calculate'
        ]

# Singleton instance
_tools_layer = None

def get_tools_layer() -> ToolsLayer:
    """الحصول على instance واحد من ToolsLayer"""
    global _tools_layer
    if _tools_layer is None:
        _tools_layer = ToolsLayer()
    return _tools_layer

