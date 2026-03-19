# rag_enhancer.py: نظام تحسين البحث والاسترجاع (RAG Enhancement)
"""
نظام متقدم لتحسين البحث والاسترجاع من قواعد البيانات والإنترنت
"""
import logging
from typing import List, Dict, Any, Optional
from database import search_medical_data, search_scraped_data, get_scraped_data
import re

logger = logging.getLogger(__name__)

class RAGEnhancer:
    """نظام تحسين البحث والاسترجاع"""
    
    def __init__(self):
        self.max_context_length = 3000  # الحد الأقصى لطول السياق
        self.min_relevance_score = 3  # الحد الأدنى لدرجة التطابق
        
    def enhance_query(self, query: str) -> Dict[str, Any]:
        """تحسين استعلام البحث"""
        enhanced = {
            'original_query': query,
            'keywords': [],
            'expanded_queries': [],
            'medical_terms': [],
        }
        
        # استخراج الكلمات المفتاحية
        words = re.findall(r'\b\w+\b', query.lower())
        enhanced['keywords'] = [w for w in words if len(w) > 2]
        
        # توسيع الاستعلام بكلمات مشابهة
        synonyms_map = {
            'دواء': ['علاج', 'دواء', 'دواء', 'أدوية'],
            'مرض': ['مرض', 'حالة', 'مشكلة صحية'],
            'ألم': ['ألم', 'وجع', 'مضض'],
            'علاج': ['علاج', 'دواء', 'شفاء'],
        }
        
        expanded = [query]
        for word in enhanced['keywords']:
            if word in synonyms_map:
                for synonym in synonyms_map[word]:
                    if synonym not in query.lower():
                        expanded.append(query.replace(word, synonym))
        
        enhanced['expanded_queries'] = expanded[:3]  # أول 3 استعلامات موسعة
        
        # اكتشاف المصطلحات الطبية
        medical_keywords = ['دواء', 'مرض', 'علاج', 'جرعة', 'أعراض', 'مضاعفات', 'موانع']
        enhanced['medical_terms'] = [w for w in enhanced['keywords'] if w in medical_keywords]
        
        return enhanced
    
    def search_enhanced(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """بحث محسّن يجمع من مصادر متعددة"""
        results = []
        
        # 1. تحسين الاستعلام
        enhanced_query = self.enhance_query(query)
        
        # 2. البحث في قاعدة البيانات الطبية (الأولوية الأولى)
        try:
            medical_results = search_medical_data(query, limit=limit)
            for result in medical_results:
                if result.get('relevance_score', 0) >= self.min_relevance_score:
                    result['source_type'] = 'medical_db'
                    result['priority'] = 1  # أولوية عالية
                    results.append(result)
        except Exception as e:
            logger.debug(f"Medical search error: {e}")
        
        # 3. البحث في البيانات المستخرجة
        try:
            scraped_results = search_scraped_data(query, limit=limit)
            for result in scraped_results:
                if result.get('relevance_score', 0) >= self.min_relevance_score:
                    result['source_type'] = 'scraped_db'
                    result['priority'] = 2
                    results.append(result)
        except Exception as e:
            logger.debug(f"Scraped data search error: {e}")
        
        # 4. البحث الموسع (إذا لم توجد نتائج كافية)
        if len(results) < limit and enhanced_query.get('expanded_queries'):
            for expanded_query in enhanced_query['expanded_queries'][:2]:
                try:
                    expanded_medical = search_medical_data(expanded_query, limit=2)
                    for result in expanded_medical:
                        if result.get('relevance_score', 0) >= self.min_relevance_score - 1:
                            result['source_type'] = 'medical_db_expanded'
                            result['priority'] = 3
                            # تجنب التكرار
                            if not any(r.get('id') == result.get('id') for r in results):
                                results.append(result)
                except:
                    pass
        
        # ترتيب النتائج حسب الأولوية ودرجة التطابق
        results.sort(key=lambda x: (
            x.get('priority', 99),
            -x.get('relevance_score', 0)
        ))
        
        return results[:limit]
    
    def format_context(self, results: List[Dict[str, Any]], max_length: int = None) -> str:
        """تنسيق النتائج كسياق للـ LLM"""
        if not results:
            return ""
        
        max_length = max_length or self.max_context_length
        context_parts = []
        current_length = 0
        
        for result in results:
            # بناء جزء السياق
            part = ""
            
            # العنوان
            title = result.get('title', '')
            if title:
                part += f"**{title}**\n"
            
            # المحتوى
            content = result.get('content', '') or result.get('description', '')
            if content:
                # تقليل المحتوى إذا كان طويلاً
                if len(content) > 500:
                    content = content[:500] + "..."
                part += f"{content}\n"
            
            # معلومات إضافية للبيانات الطبية
            if result.get('source_type') == 'medical_db':
                dosage = result.get('dosage', '')
                if dosage:
                    part += f"💉 الجرعة: {dosage}\n"
                
                side_effects = result.get('side_effects', '')
                if side_effects:
                    part += f"⚠️ الآثار الجانبية: {side_effects}\n"
            
            # الرابط
            url = result.get('url', '')
            if url:
                part += f"🔗 {url}\n"
            
            part += "\n"
            
            # التحقق من الطول
            if current_length + len(part) > max_length:
                break
            
            context_parts.append(part)
            current_length += len(part)
        
        return "\n".join(context_parts)
    
    def get_best_context(self, query: str, max_length: int = None) -> str:
        """الحصول على أفضل سياق للاستعلام"""
        results = self.search_enhanced(query, limit=5)
        return self.format_context(results, max_length)

# Singleton instance
_rag_enhancer = None

def get_rag_enhancer() -> RAGEnhancer:
    """الحصول على instance موحد من RAGEnhancer"""
    global _rag_enhancer
    if _rag_enhancer is None:
        _rag_enhancer = RAGEnhancer()
    return _rag_enhancer

