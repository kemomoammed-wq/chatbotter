# training_data_exporter.py: تصدير البيانات التدريبية بصيغ مختلفة للتدريب
"""
نظام تصدير البيانات التدريبية بصيغ مختلفة للاستخدام في تدريب النماذج
"""
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from training_enhancer import get_training_enhancer
from database import get_training_samples, Session, TrainingSample

logger = logging.getLogger(__name__)

class TrainingDataExporter:
    """نظام تصدير البيانات التدريبية"""
    
    def __init__(self):
        self.enhancer = get_training_enhancer()
    
    def export_for_openai_finetuning(self, output_file: str = 'openai_training.jsonl',
                                     user_id: Optional[str] = None, limit: int = 1000) -> int:
        """تصدير البيانات بصيغة OpenAI Fine-tuning"""
        try:
            samples = self.enhancer.get_high_quality_samples(user_id=user_id, limit=limit)
            
            if not samples:
                logger.warning("No high quality samples found")
                return 0
            
            count = 0
            with open(output_file, 'w', encoding='utf-8') as f:
                for sample in samples:
                    entry = {
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'أنت مساعد ذكي ومفيد. تجيب على الأسئلة بدقة ووضوح.'
                            },
                            {
                                'role': 'user',
                                'content': sample['message']
                            },
                            {
                                'role': 'assistant',
                                'content': sample['response']
                            }
                        ]
                    }
                    
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    count += 1
            
            logger.info(f"✅ Exported {count} samples for OpenAI fine-tuning to {output_file}")
            return count
            
        except Exception as e:
            logger.error(f"Error exporting for OpenAI: {e}", exc_info=True)
            return 0
    
    def export_for_chatgpt_training(self, output_file: str = 'chatgpt_training.jsonl',
                                    user_id: Optional[str] = None, limit: int = 1000) -> int:
        """تصدير البيانات بصيغة ChatGPT Training"""
        try:
            samples = self.enhancer.get_high_quality_samples(user_id=user_id, limit=limit)
            
            if not samples:
                logger.warning("No high quality samples found")
                return 0
            
            count = 0
            with open(output_file, 'w', encoding='utf-8') as f:
                for sample in samples:
                    # تنسيق ChatGPT
                    entry = {
                        'conversation': [
                            {
                                'from': 'human',
                                'value': sample['message']
                            },
                            {
                                'from': 'gpt',
                                'value': sample['response']
                            }
                        ],
                        'metadata': {
                            'quality_score': sample.get('quality_score', 0),
                            'intent': sample.get('intent'),
                            'sentiment': sample.get('sentiment'),
                            'search_count': sample.get('search_results', {}).get('search_count', 0),
                        }
                    }
                    
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    count += 1
            
            logger.info(f"✅ Exported {count} samples for ChatGPT training to {output_file}")
            return count
            
        except Exception as e:
            logger.error(f"Error exporting for ChatGPT: {e}", exc_info=True)
            return 0
    
    def export_statistics(self, output_file: str = 'training_statistics.json',
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """تصدير إحصائيات البيانات التدريبية"""
        try:
            analysis = self.enhancer.analyze_training_data(user_id=user_id)
            
            # إحصائيات إضافية
            session = Session()
            query = session.query(TrainingSample)
            if user_id:
                query = query.filter(TrainingSample.user_id == user_id)
            
            total = query.count()
            
            # حسب intent
            intents = {}
            samples = query.limit(1000).all()
            for sample in samples:
                search_data = json.loads(sample.search_results) if sample.search_results else {}
                intent = search_data.get('intent', 'general')
                intents[intent] = intents.get(intent, 0) + 1
            
            stats = {
                'total_samples': total,
                'quality_analysis': analysis,
                'intent_distribution': intents,
                'exported_at': datetime.now(timezone.utc).isoformat(),
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            session.close()
            logger.info(f"✅ Exported statistics to {output_file}")
            return stats
            
        except Exception as e:
            logger.error(f"Error exporting statistics: {e}", exc_info=True)
            return {}

# Singleton instance
_exporter = None

def get_training_exporter() -> TrainingDataExporter:
    """الحصول على instance موحد من TrainingDataExporter"""
    global _exporter
    if _exporter is None:
        _exporter = TrainingDataExporter()
    return _exporter

