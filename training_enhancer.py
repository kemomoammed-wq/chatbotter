# training_enhancer.py: نظام تحسين التدريب من البيانات المحفوظة
"""
نظام متقدم لتحسين جودة البيانات التدريبية وتحسين أداء الشات بوت
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from database import get_training_samples, TrainingSample, Session
import re

logger = logging.getLogger(__name__)

class TrainingEnhancer:
    """نظام تحسين البيانات التدريبية"""
    
    def __init__(self):
        self.min_quality_score = 0.6  # الحد الأدنى لجودة العينة
        self.max_samples_per_user = 1000  # الحد الأقصى للعينات لكل مستخدم
        
    def calculate_quality_score(self, sample: Dict[str, Any]) -> float:
        """حساب درجة جودة العينة التدريبية"""
        score = 0.0
        
        # 1. طول الرسالة (10%)
        message_len = len(sample.get('message', ''))
        if 10 <= message_len <= 500:
            score += 0.1
        elif message_len > 500:
            score += 0.05
        
        # 2. طول الرد (15%)
        response_len = len(sample.get('response', ''))
        if 20 <= response_len <= 2000:
            score += 0.15
        elif response_len > 2000:
            score += 0.1
        
        # 3. وجود نتائج بحث (20%)
        search_results = sample.get('search_results', {})
        if isinstance(search_results, str):
            try:
                search_results = json.loads(search_results)
            except:
                search_results = {}
        
        search_count = search_results.get('search_count', 0)
        if search_count > 0:
            score += 0.2
        elif search_count >= 2:
            score += 0.25
        
        # 4. وجود intent و sentiment (15%)
        if sample.get('intent') and sample.get('intent') != 'general':
            score += 0.1
        if sample.get('sentiment') and sample.get('sentiment') != 'neutral':
            score += 0.05
        
        # 5. confidence score (10%)
        confidence = sample.get('confidence', 0.0)
        if isinstance(confidence, (int, float)):
            score += min(confidence * 0.1, 0.1)
        
        # 6. جودة المحتوى (20%)
        message = sample.get('message', '').lower()
        response = sample.get('response', '').lower()
        
        # التحقق من وجود كلمات مفيدة
        useful_words = ['ما', 'كيف', 'لماذا', 'متى', 'أين', 'ماذا', 'هل', 'شرح', 'معلومات']
        if any(word in message for word in useful_words):
            score += 0.1
        
        # التحقق من أن الرد ليس فارغاً أو قصير جداً
        if len(response) > 50 and len(response.split()) > 5:
            score += 0.1
        
        # 7. وجود tags (10%)
        tags = sample.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        
        if tags and len(tags) > 0:
            score += min(len(tags) * 0.05, 0.1)
        
        return min(score, 1.0)
    
    def enhance_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """تحسين عينة تدريبية واحدة"""
        enhanced = sample.copy()
        
        # تنظيف الرسالة
        message = enhanced.get('message', '').strip()
        message = re.sub(r'\s+', ' ', message)  # إزالة المسافات الزائدة
        enhanced['message'] = message
        
        # تنظيف الرد
        response = enhanced.get('response', '').strip()
        response = re.sub(r'\s+', ' ', response)
        enhanced['response'] = response
        
        # تحسين نتائج البحث
        search_results = enhanced.get('search_results', {})
        if isinstance(search_results, str):
            try:
                search_results = json.loads(search_results)
            except:
                search_results = {}
        
        # إضافة metadata محسّن
        if not enhanced.get('quality_score'):
            enhanced['quality_score'] = self.calculate_quality_score(enhanced)
        
        # إضافة timestamp محسّن
        if not enhanced.get('enhanced_at'):
            enhanced['enhanced_at'] = datetime.now(timezone.utc).isoformat()
        
        return enhanced
    
    def get_high_quality_samples(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """الحصول على عينات عالية الجودة للتدريب"""
        try:
            session = Session()
            query = session.query(TrainingSample).order_by(TrainingSample.timestamp.desc())
            
            if user_id:
                query = query.filter(TrainingSample.user_id == user_id)
            
            samples = query.limit(limit * 2).all()  # جلب ضعف العدد للفلترة
            
            enhanced_samples = []
            for sample in samples:
                sample_dict = {
                    'id': sample.id,
                    'user_id': sample.user_id,
                    'message': sample.message,
                    'response': sample.response,
                    'search_results': json.loads(sample.search_results) if sample.search_results else {},
                    'tags': sample.tags.split(',') if sample.tags else [],
                    'timestamp': sample.timestamp.isoformat() if sample.timestamp else None,
                }
                
                # حساب درجة الجودة
                quality_score = self.calculate_quality_score(sample_dict)
                sample_dict['quality_score'] = quality_score
                
                # فلترة حسب الجودة
                if quality_score >= self.min_quality_score:
                    enhanced = self.enhance_sample(sample_dict)
                    enhanced_samples.append(enhanced)
            
            # ترتيب حسب الجودة
            enhanced_samples.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            session.close()
            return enhanced_samples[:limit]
            
        except Exception as e:
            logger.error(f"Error getting high quality samples: {e}", exc_info=True)
            return []
    
    def generate_training_dataset(self, output_file: str = 'training_data_enhanced.jsonl', 
                                  user_id: Optional[str] = None, limit: int = 500) -> int:
        """إنشاء ملف بيانات تدريبية محسّنة بصيغة JSONL"""
        try:
            samples = self.get_high_quality_samples(user_id=user_id, limit=limit)
            
            if not samples:
                logger.warning("No high quality samples found")
                return 0
            
            count = 0
            with open(output_file, 'w', encoding='utf-8') as f:
                for sample in samples:
                    # تنسيق البيانات للتدريب
                    training_entry = {
                        'messages': [
                            {
                                'role': 'user',
                                'content': sample['message']
                            },
                            {
                                'role': 'assistant',
                                'content': sample['response']
                            }
                        ],
                        'metadata': {
                            'user_id': sample.get('user_id'),
                            'quality_score': sample.get('quality_score', 0),
                            'intent': sample.get('intent'),
                            'sentiment': sample.get('sentiment'),
                            'confidence': sample.get('confidence'),
                            'search_count': sample.get('search_results', {}).get('search_count', 0),
                            'tags': sample.get('tags', []),
                            'timestamp': sample.get('timestamp'),
                        }
                    }
                    
                    f.write(json.dumps(training_entry, ensure_ascii=False) + '\n')
                    count += 1
            
            logger.info(f"✅ Generated {count} enhanced training samples in {output_file}")
            return count
            
        except Exception as e:
            logger.error(f"Error generating training dataset: {e}", exc_info=True)
            return 0
    
    def analyze_training_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """تحليل البيانات التدريبية"""
        try:
            session = Session()
            query = session.query(TrainingSample)
            
            if user_id:
                query = query.filter(TrainingSample.user_id == user_id)
            
            total_samples = query.count()
            
            # تحليل الجودة
            all_samples = query.limit(1000).all()
            quality_scores = []
            
            for sample in all_samples:
                sample_dict = {
                    'message': sample.message,
                    'response': sample.response,
                    'search_results': json.loads(sample.search_results) if sample.search_results else {},
                    'tags': sample.tags.split(',') if sample.tags else [],
                }
                score = self.calculate_quality_score(sample_dict)
                quality_scores.append(score)
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            high_quality_count = sum(1 for s in quality_scores if s >= self.min_quality_score)
            
            session.close()
            
            return {
                'total_samples': total_samples,
                'analyzed_samples': len(quality_scores),
                'average_quality_score': round(avg_quality, 3),
                'high_quality_count': high_quality_count,
                'high_quality_percentage': round((high_quality_count / len(quality_scores) * 100) if quality_scores else 0, 2),
                'min_quality_threshold': self.min_quality_score,
            }
            
        except Exception as e:
            logger.error(f"Error analyzing training data: {e}", exc_info=True)
            return {}

# Singleton instance
_training_enhancer = None

def get_training_enhancer() -> TrainingEnhancer:
    """الحصول على instance موحد من TrainingEnhancer"""
    global _training_enhancer
    if _training_enhancer is None:
        _training_enhancer = TrainingEnhancer()
    return _training_enhancer

