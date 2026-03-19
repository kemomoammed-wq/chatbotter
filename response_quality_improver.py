# response_quality_improver.py: نظام تحسين جودة الردود تلقائياً
"""
نظام متقدم لتحسين جودة الردود وتحليلها تلقائياً
"""
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from database import get_training_samples, save_training_sample, Session, TrainingSample
import json

logger = logging.getLogger(__name__)

class ResponseQualityImprover:
    """نظام تحسين جودة الردود"""
    
    def __init__(self):
        self.min_response_length = 20
        self.max_response_length = 3000
        self.quality_threshold = 0.7
        
    def analyze_response_quality(self, message: str, response: str, 
                                search_results: Optional[List[Dict]] = None,
                                intent: Optional[str] = None,
                                sentiment: Optional[str] = None) -> Dict[str, Any]:
        """تحليل جودة الرد"""
        analysis = {
            'quality_score': 0.0,
            'issues': [],
            'suggestions': [],
            'strengths': [],
        }
        
        # 1. طول الرد
        response_len = len(response)
        if response_len < self.min_response_length:
            analysis['issues'].append(f"الرد قصير جداً ({response_len} حرف)")
            analysis['quality_score'] -= 0.2
        elif response_len > self.max_response_length:
            analysis['issues'].append(f"الرد طويل جداً ({response_len} حرف)")
            analysis['quality_score'] -= 0.1
        else:
            analysis['strengths'].append(f"طول مناسب ({response_len} حرف)")
            analysis['quality_score'] += 0.1
        
        # 2. وجود معلومات من البحث
        if search_results and len(search_results) > 0:
            analysis['strengths'].append(f"يحتوي على معلومات من {len(search_results)} مصدر")
            analysis['quality_score'] += 0.2
        else:
            analysis['suggestions'].append("يمكن إضافة معلومات من البحث لتحسين الجودة")
        
        # 3. التنوع في المحتوى
        words = response.split()
        unique_words = len(set(words))
        diversity_ratio = unique_words / len(words) if words else 0
        
        if diversity_ratio > 0.6:
            analysis['strengths'].append("محتوى متنوع")
            analysis['quality_score'] += 0.1
        else:
            analysis['issues'].append("المحتوى متكرر")
            analysis['quality_score'] -= 0.1
        
        # 4. وجود جمل كاملة
        sentences = re.split(r'[.!?]\s+', response)
        if len(sentences) >= 2:
            analysis['strengths'].append(f"يحتوي على {len(sentences)} جملة")
            analysis['quality_score'] += 0.1
        else:
            analysis['issues'].append("يحتوي على جملة واحدة فقط")
        
        # 5. وجود معلومات مفيدة (كلمات مفتاحية)
        useful_keywords = ['معلومات', 'شرح', 'تفاصيل', 'نصائح', 'نصيحة', 'يمكن', 'يجب', 'ينصح']
        found_keywords = sum(1 for kw in useful_keywords if kw in response.lower())
        if found_keywords > 0:
            analysis['strengths'].append(f"يحتوي على {found_keywords} كلمة مفتاحية مفيدة")
            analysis['quality_score'] += 0.1
        
        # 6. التنسيق والبنية
        if '\n' in response or '•' in response or '-' in response:
            analysis['strengths'].append("منسق بشكل جيد")
            analysis['quality_score'] += 0.1
        
        # 7. وجود intent و sentiment
        if intent and intent != 'general':
            analysis['strengths'].append(f"Intent محدد: {intent}")
            analysis['quality_score'] += 0.05
        
        if sentiment and sentiment != 'neutral':
            analysis['strengths'].append(f"Sentiment محدد: {sentiment}")
            analysis['quality_score'] += 0.05
        
        # تطبيع النتيجة
        analysis['quality_score'] = max(0.0, min(1.0, analysis['quality_score']))
        
        # تحديد التصنيف
        if analysis['quality_score'] >= 0.8:
            analysis['category'] = 'excellent'
        elif analysis['quality_score'] >= 0.6:
            analysis['category'] = 'good'
        elif analysis['quality_score'] >= 0.4:
            analysis['category'] = 'fair'
        else:
            analysis['category'] = 'poor'
        
        return analysis
    
    def improve_response(self, message: str, response: str, 
                        search_results: Optional[List[Dict]] = None) -> str:
        """تحسين الرد تلقائياً"""
        improved = response
        
        # 1. إضافة معلومات من البحث إذا كانت مفقودة
        if search_results and len(search_results) > 0:
            # التحقق من وجود معلومات البحث في الرد
            has_search_info = any(
                result.get('title', '').lower() in response.lower() or
                result.get('url', '') in response
                for result in search_results[:3]
            )
            
            if not has_search_info and len(response) < 500:
                # إضافة معلومات من البحث
                improved += "\n\n📚 مصادر إضافية:\n"
                for i, result in enumerate(search_results[:2], 1):
                    title = result.get('title', '')
                    url = result.get('url', '')
                    if title:
                        improved += f"{i}. {title}\n"
                    if url:
                        improved += f"   🔗 {url}\n"
        
        # 2. تحسين التنسيق
        if '\n\n' not in improved and len(improved) > 200:
            # إضافة فواصل للقراءة الأسهل
            sentences = re.split(r'[.!?]\s+', improved)
            if len(sentences) > 3:
                improved = '.\n\n'.join(sentences[:len(sentences)//2]) + '.\n\n' + '.\n\n'.join(sentences[len(sentences)//2:])
        
        # 3. إزالة التكرار
        lines = improved.split('\n')
        seen = set()
        unique_lines = []
        for line in lines:
            line_lower = line.lower().strip()
            if line_lower and line_lower not in seen:
                seen.add(line_lower)
                unique_lines.append(line)
        improved = '\n'.join(unique_lines)
        
        return improved.strip()
    
    def should_save_as_training(self, message: str, response: str,
                               quality_analysis: Dict[str, Any]) -> bool:
        """تحديد ما إذا كان يجب حفظ الرد كعينة تدريبية"""
        # حفظ إذا كانت الجودة عالية
        if quality_analysis.get('quality_score', 0) >= self.quality_threshold:
            return True
        
        # حفظ إذا كان الرد يحتوي على معلومات مفيدة
        if quality_analysis.get('strengths'):
            strengths_count = len(quality_analysis['strengths'])
            if strengths_count >= 3:
                return True
        
        # عدم الحفظ إذا كانت هناك مشاكل كثيرة
        if len(quality_analysis.get('issues', [])) > 2:
            return False
        
        return False
    
    def process_and_save(self, user_id: str, message: str, response: str,
                        search_results: Optional[List[Dict]] = None,
                        intent: Optional[str] = None,
                        sentiment: Optional[str] = None,
                        confidence: Optional[float] = None) -> Dict[str, Any]:
        """معالجة وحفظ الرد مع التحسين"""
        # تحليل الجودة
        quality_analysis = self.analyze_response_quality(
            message, response, search_results, intent, sentiment
        )
        
        # تحسين الرد إذا لزم الأمر
        improved_response = response
        if quality_analysis.get('quality_score', 0) < self.quality_threshold:
            improved_response = self.improve_response(message, response, search_results)
            # إعادة التحليل بعد التحسين
            quality_analysis = self.analyze_response_quality(
                message, improved_response, search_results, intent, sentiment
            )
        
        # حفظ كعينة تدريبية إذا كانت الجودة عالية
        saved = False
        if self.should_save_as_training(message, improved_response, quality_analysis):
            try:
                save_training_sample(
                    user_id=user_id,
                    message=message,
                    response=improved_response,
                    search_results=search_results,
                    intent=intent,
                    sentiment=sentiment,
                    confidence=confidence or quality_analysis.get('quality_score', 0.8),
                )
                saved = True
                logger.info(f"✅ Saved high-quality training sample (score: {quality_analysis.get('quality_score', 0):.2f})")
            except Exception as e:
                logger.warning(f"Failed to save training sample: {e}")
        
        return {
            'original_response': response,
            'improved_response': improved_response,
            'quality_analysis': quality_analysis,
            'saved_as_training': saved,
            'was_improved': improved_response != response,
        }

# Singleton instance
_response_improver = None

def get_response_improver() -> ResponseQualityImprover:
    """الحصول على instance موحد من ResponseQualityImprover"""
    global _response_improver
    if _response_improver is None:
        _response_improver = ResponseQualityImprover()
    return _response_improver

