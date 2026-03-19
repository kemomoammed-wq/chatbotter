# scraper_manager.py: مدير متقدم لاستخراج البيانات مع batch processing وأولويات
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import PriorityQueue
import time
from datetime import datetime, timedelta
from web_scraper import get_web_scraper
from database import save_scraped_data, get_scraped_data
from web_scraper_utils import get_data_manager

logger = logging.getLogger(__name__)

class ScraperManager:
    """مدير متقدم لاستخراج البيانات مع batch processing وأولويات"""
    
    def __init__(self, max_workers: int = 3):
        self.scraper = get_web_scraper()
        self.data_manager = get_data_manager()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.priority_queue = PriorityQueue()
        self.processing_urls = set()
        self.completed_urls = {}
        self.failed_urls = {}
        
    def add_url(self, url: str, priority: int = 5, callback: Optional[Callable] = None, 
                force_refresh: bool = False, metadata: Dict = None):
        """إضافة رابط للقائمة مع أولوية"""
        # الأولوية: 1 = عالي، 5 = متوسط، 10 = منخفض
        if url not in self.processing_urls:
            self.priority_queue.put((priority, time.time(), {
                'url': url,
                'callback': callback,
                'force_refresh': force_refresh,
                'metadata': metadata or {}
            }))
            logger.info(f"تم إضافة رابط للقائمة: {url} (أولوية: {priority})")
    
    def process_url(self, url_info: Dict) -> Dict[str, Any]:
        """معالجة رابط واحد"""
        url = url_info['url']
        force_refresh = url_info.get('force_refresh', False)
        metadata = url_info.get('metadata', {})
        
        try:
            self.processing_urls.add(url)
            logger.info(f"بدء معالجة: {url}")
            
            # استخراج البيانات
            result = self.scraper.scrape_url(url, force_refresh=force_refresh)
            
            if result.get('success'):
                # حفظ البيانات
                save_result = save_scraped_data(
                    url=url,
                    title=result.get('title', ''),
                    description=result.get('description', ''),
                    content=result.get('content', ''),
                    source=result.get('source', 'general'),
                    metadata=result.get('webteb_data') or result.get('wikipedia_data') or metadata
                )
                
                result['saved'] = save_result
                self.completed_urls[url] = {
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                
                # استدعاء callback إذا كان موجوداً
                callback = url_info.get('callback')
                if callback:
                    try:
                        callback(url, result)
                    except Exception as e:
                        logger.error(f"خطأ في callback: {e}")
                
                logger.info(f"تم معالجة بنجاح: {url}")
            else:
                self.failed_urls[url] = {
                    'error': result.get('error', 'خطأ غير معروف'),
                    'timestamp': datetime.now().isoformat()
                }
                logger.error(f"فشل معالجة: {url} - {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في معالجة {url}: {e}")
            self.failed_urls[url] = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return {'success': False, 'error': str(e), 'url': url}
        finally:
            self.processing_urls.discard(url)
    
    def process_batch(self, urls: List[str], priorities: List[int] = None, 
                     force_refresh: bool = False) -> Dict[str, Any]:
        """معالجة مجموعة من الروابط"""
        if priorities is None:
            priorities = [5] * len(urls)
        
        # إضافة جميع الروابط للقائمة
        for url, priority in zip(urls, priorities):
            self.add_url(url, priority=priority, force_refresh=force_refresh)
        
        # معالجة الروابط
        results = []
        futures = []
        
        while not self.priority_queue.empty():
            priority, timestamp, url_info = self.priority_queue.get()
            future = self.executor.submit(self.process_url, url_info)
            futures.append(future)
        
        # جمع النتائج
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"خطأ في future: {e}")
        
        return {
            'total': len(urls),
            'successful': len([r for r in results if r.get('success')]),
            'failed': len([r for r in results if not r.get('success')]),
            'results': results
        }
    
    def process_urls_async(self, urls: List[str], callback: Optional[Callable] = None) -> Dict[str, Any]:
        """معالجة روابط بشكل غير متزامن"""
        async def process_all():
            tasks = []
            for url in urls:
                task = asyncio.to_thread(self.scraper.scrape_url, url)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        return asyncio.run(process_all())
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة المعالج"""
        return {
            'queue_size': self.priority_queue.qsize(),
            'processing': list(self.processing_urls),
            'completed_count': len(self.completed_urls),
            'failed_count': len(self.failed_urls),
            'recent_completed': list(self.completed_urls.keys())[-10:],
            'recent_failed': list(self.failed_urls.keys())[-10:]
        }
    
    def retry_failed(self, max_retries: int = 3) -> Dict[str, Any]:
        """إعادة محاولة الروابط الفاشلة"""
        retry_results = []
        urls_to_retry = list(self.failed_urls.keys())
        
        for url in urls_to_retry:
            for attempt in range(max_retries):
                result = self.process_url({
                    'url': url,
                    'force_refresh': True,
                    'metadata': {}
                })
                if result.get('success'):
                    retry_results.append({'url': url, 'success': True, 'attempt': attempt + 1})
                    break
                else:
                    retry_results.append({'url': url, 'success': False, 'attempt': attempt + 1, 
                                        'error': result.get('error')})
        
        return {
            'total_retried': len(urls_to_retry),
            'successful': len([r for r in retry_results if r.get('success')]),
            'results': retry_results
        }
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """تنظيف البيانات القديمة"""
        old_records = self.data_manager.find_old_records(days=days)
        # يمكن إضافة منطق الحذف هنا
        return len(old_records)
    
    def get_analytics(self) -> Dict[str, Any]:
        """الحصول على تحليلات شاملة"""
        stats = self.data_manager.get_statistics()
        status = self.get_status()
        
        return {
            'database_stats': stats,
            'processor_status': status,
            'success_rate': (
                len(self.completed_urls) / 
                (len(self.completed_urls) + len(self.failed_urls)) * 100
                if (len(self.completed_urls) + len(self.failed_urls)) > 0 else 0
            )
        }

# إنشاء instance عام
_scraper_manager = None

def get_scraper_manager() -> ScraperManager:
    """الحصول على instance من ScraperManager"""
    global _scraper_manager
    if _scraper_manager is None:
        _scraper_manager = ScraperManager()
    return _scraper_manager

