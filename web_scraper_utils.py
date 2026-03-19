# web_scraper_utils.py: أدوات مساعدة لاستخراج البيانات
import json
import csv
from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import get_scraped_data, search_scraped_data
import logging

logger = logging.getLogger(__name__)

class ScrapedDataManager:
    """مدير البيانات المستخرجة - ميزات متقدمة"""
    
    def export_to_json(self, output_file: str = 'data/scraped_data_export.json', 
                      source: str = None, limit: int = None) -> bool:
        """تصدير البيانات إلى ملف JSON"""
        try:
            data = get_scraped_data(source=source, limit=limit or 1000)
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_records': len(data),
                'source_filter': source,
                'data': data
            }
            
            import os
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم تصدير {len(data)} سجل إلى {output_file}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تصدير البيانات: {e}")
            return False
    
    def export_to_csv(self, output_file: str = 'data/scraped_data_export.csv',
                     source: str = None, limit: int = None) -> bool:
        """تصدير البيانات إلى ملف CSV"""
        try:
            data = get_scraped_data(source=source, limit=limit or 1000)
            
            if not data:
                logger.warning("لا توجد بيانات للتصدير")
                return False
            
            import os
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'url', 'title', 'description', 
                                                       'source', 'timestamp'])
                writer.writeheader()
                for record in data:
                    writer.writerow({
                        'id': record.get('id'),
                        'url': record.get('url'),
                        'title': record.get('title', '')[:200],
                        'description': record.get('description', '')[:500],
                        'source': record.get('source'),
                        'timestamp': record.get('timestamp')
                    })
            
            logger.info(f"تم تصدير {len(data)} سجل إلى {output_file}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تصدير البيانات: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات البيانات المحفوظة"""
        try:
            all_data = get_scraped_data(limit=10000)
            
            stats = {
                'total_records': len(all_data),
                'by_source': {},
                'recent_updates': 0,
                'oldest_record': None,
                'newest_record': None,
                'avg_content_length': 0,
                'total_content_length': 0
            }
            
            if not all_data:
                return stats
            
            # إحصائيات حسب المصدر
            for record in all_data:
                source = record.get('source', 'unknown')
                stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
                
                # طول المحتوى
                content_len = len(record.get('content', ''))
                stats['total_content_length'] += content_len
            
            # السجلات الحديثة (آخر 24 ساعة)
            now = datetime.now()
            for record in all_data:
                if record.get('timestamp'):
                    try:
                        record_time = datetime.fromisoformat(record['timestamp'])
                        if (now - record_time).total_seconds() < 86400:  # 24 ساعة
                            stats['recent_updates'] += 1
                    except:
                        pass
            
            # أقدم وأحدث سجل
            timestamps = [r.get('timestamp') for r in all_data if r.get('timestamp')]
            if timestamps:
                try:
                    timestamps_dt = [datetime.fromisoformat(ts) for ts in timestamps]
                    stats['oldest_record'] = min(timestamps_dt).isoformat()
                    stats['newest_record'] = max(timestamps_dt).isoformat()
                except:
                    pass
            
            # متوسط طول المحتوى
            if stats['total_records'] > 0:
                stats['avg_content_length'] = stats['total_content_length'] // stats['total_records']
            
            return stats
        except Exception as e:
            logger.error(f"خطأ في حساب الإحصائيات: {e}")
            return {}
    
    def find_old_records(self, days: int = 30) -> List[Dict[str, Any]]:
        """العثور على السجلات القديمة (أقدم من عدد محدد من الأيام)"""
        try:
            all_data = get_scraped_data(limit=10000)
            cutoff_date = datetime.now() - timedelta(days=days)
            old_records = []
            
            for record in all_data:
                if record.get('timestamp'):
                    try:
                        record_time = datetime.fromisoformat(record['timestamp'])
                        if record_time < cutoff_date:
                            old_records.append(record)
                    except:
                        pass
            
            return old_records
        except Exception as e:
            logger.error(f"خطأ في البحث عن السجلات القديمة: {e}")
            return []
    
    def cleanup_duplicates(self) -> int:
        """تنظيف السجلات المكررة (نفس الرابط)"""
        try:
            from database import Session, ScrapedData
            from sqlalchemy import func
            
            session = Session()
            
            # العثور على الروابط المكررة
            duplicates = session.query(
                ScrapedData.url,
                func.count(ScrapedData.id).label('count')
            ).group_by(ScrapedData.url).having(func.count(ScrapedData.id) > 1).all()
            
            removed_count = 0
            for url, count in duplicates:
                # الاحتفاظ بأحدث سجل فقط
                records = session.query(ScrapedData).filter_by(url=url).order_by(
                    ScrapedData.timestamp.desc()
                ).all()
                
                # حذف السجلات القديمة
                for record in records[1:]:
                    session.delete(record)
                    removed_count += 1
            
            session.commit()
            session.close()
            
            logger.info(f"تم حذف {removed_count} سجل مكرر")
            return removed_count
        except Exception as e:
            logger.error(f"خطأ في تنظيف المكررات: {e}")
            return 0
    
    def search_advanced(self, query: str, source: str = None, 
                       min_content_length: int = None,
                       date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """بحث متقدم في البيانات"""
        try:
            results = search_scraped_data(query, limit=100)
            
            # فلترة حسب المصدر
            if source:
                results = [r for r in results if r.get('source') == source]
            
            # فلترة حسب طول المحتوى
            if min_content_length:
                results = [r for r in results if len(r.get('content', '')) >= min_content_length]
            
            # فلترة حسب التاريخ
            if date_from or date_to:
                filtered_results = []
                for r in results:
                    if r.get('timestamp'):
                        try:
                            record_time = datetime.fromisoformat(r['timestamp'])
                            if date_from:
                                from_date = datetime.fromisoformat(date_from)
                                if record_time < from_date:
                                    continue
                            if date_to:
                                to_date = datetime.fromisoformat(date_to)
                                if record_time > to_date:
                                    continue
                            filtered_results.append(r)
                        except:
                            pass
                results = filtered_results
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث المتقدم: {e}")
            return []

# إنشاء instance عام
_data_manager = None

def get_data_manager() -> ScrapedDataManager:
    """الحصول على instance من ScrapedDataManager"""
    global _data_manager
    if _data_manager is None:
        _data_manager = ScrapedDataManager()
    return _data_manager

