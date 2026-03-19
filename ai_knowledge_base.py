# ai_knowledge_base.py: قاعدة معرفة شاملة للذكاء الاصطناعي من AI_MASTER_ROADMAP.md
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AIKnowledgeBase:
    """قاعدة معرفة شاملة للذكاء الاصطناعي من الدليل الشامل"""
    
    def __init__(self, roadmap_path: str = "AI_MASTER_ROADMAP.md"):
        self.roadmap_path = Path(roadmap_path)
        self.knowledge = {}
        self.sections = {}
        self.keywords_index = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """تحميل المحتوى من ملف الدليل"""
        try:
            if not self.roadmap_path.exists():
                logger.warning(f"Roadmap file not found: {self.roadmap_path}")
                self._load_default_knowledge()
                return
            
            with open(self.roadmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # استخراج الأبواب والمحتوى
            self._parse_markdown(content)
            self._build_keywords_index()
            logger.info(f"Loaded {len(self.sections)} sections from knowledge base")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self._load_default_knowledge()
    
    def _parse_markdown(self, content: str):
        """تحليل ملف Markdown واستخراج المحتوى"""
        # تقسيم إلى أقسام حسب الباب
        sections_pattern = r'##\s+[🎯🌿🔧📚🧮🧠🛠️💡🎨🎮📝👁️🔒🚀🔗🧩🎭🌐✍️🛡️🌍🧠🔐💼🔮📊🎓✅]+\s+(.+?)(?=##|\Z)'
        
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # اكتشاف عنوان الباب
            if line.startswith('## '):
                if current_section:
                    self.sections[current_section] = '\n'.join(current_content)
                # استخراج عنوان الباب
                title = line.replace('##', '').strip()
                title = re.sub(r'[🎯🌿🔧📚🧮🧠🛠️💡🎨🎮📝👁️🔒🚀🔗🧩🎭🌐✍️🛡️🌍🧠🔐💼🔮📊🎓✅]', '', title).strip()
                current_section = title
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # حفظ آخر قسم
        if current_section:
            self.sections[current_section] = '\n'.join(current_content)
        
        # استخراج الأقسام الفرعية
        self._extract_subsections()
    
    def _extract_subsections(self):
        """استخراج الأقسام الفرعية والمحتوى التفصيلي"""
        for section_title, section_content in self.sections.items():
            # استخراج العناوين الفرعية (###)
            subsections = re.findall(r'###\s+(.+?)(?=\n|\Z)', section_content, re.DOTALL)
            
            # استخراج قوائم (bullet points)
            items = re.findall(r'-\s+\*\*(.+?)\*\*:\s*(.+?)(?=\n-|\n\n|\Z)', section_content, re.DOTALL)
            
            self.knowledge[section_title] = {
                'content': section_content,
                'subsections': subsections,
                'items': items,
                'keywords': self._extract_keywords(section_content)
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """استخراج الكلمات المفتاحية من النص"""
        # إزالة التنسيق
        text = re.sub(r'\*\*|`|#', '', text)
        # تقسيم إلى كلمات
        words = re.findall(r'\b[\u0600-\u06FF\w]+\b', text, re.UNICODE)
        # إزالة الكلمات الشائعة
        stop_words = {'هو', 'في', 'من', 'على', 'إلى', 'أن', 'هذا', 'هذه', 'التي', 'الذي', 'ال', 'و', 'أو', 'إن'}
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        return keywords[:20]  # أول 20 كلمة مفتاحية
    
    def _build_keywords_index(self):
        """بناء فهرس للكلمات المفتاحية"""
        for section_title, data in self.knowledge.items():
            for keyword in data['keywords']:
                keyword_lower = keyword.lower()
                if keyword_lower not in self.keywords_index:
                    self.keywords_index[keyword_lower] = []
                self.keywords_index[keyword_lower].append({
                    'section': section_title,
                    'relevance': 1.0
                })
    
    def _load_default_knowledge(self):
        """تحميل معرفة افتراضية إذا فشل تحميل الملف"""
        self.knowledge = {
            'الأساسيات': {
                'content': 'الذكاء الاصطناعي هو فرع من علوم الحاسوب',
                'keywords': ['ذكاء', 'اصطناعي', 'تعلم', 'آلة']
            }
        }
        logger.info("Loaded default knowledge base")
    
    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """بحث في قاعدة المعرفة"""
        query_lower = query.lower()
        query_words = re.findall(r'\b[\u0600-\u06FF\w]+\b', query_lower, re.UNICODE)
        
        results = []
        seen_sections = set()
        
        # البحث في الفهرس
        for word in query_words:
            if word in self.keywords_index:
                for match in self.keywords_index[word]:
                    section = match['section']
                    if section not in seen_sections:
                        if section in self.knowledge:
                            relevance = self._calculate_relevance(query, self.knowledge[section]['content'])
                            results.append({
                                'section': section,
                                'content': self.knowledge[section]['content'][:500],  # أول 500 حرف
                                'relevance': relevance,
                                'full_content': self.knowledge[section]['content']
                            })
                            seen_sections.add(section)
        
        # البحث المباشر في المحتوى
        for section_title, data in self.knowledge.items():
            if section_title not in seen_sections:
                relevance = self._calculate_relevance(query, data['content'])
                if relevance > 0.1:  # عتبة الدقة
                    results.append({
                        'section': section_title,
                        'content': data['content'][:500],
                        'relevance': relevance,
                        'full_content': data['content']
                    })
        
        # ترتيب حسب الدقة
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:max_results]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """حساب مدى صلة المحتوى بالاستعلام"""
        query_words = set(re.findall(r'\b[\u0600-\u06FF\w]+\b', query.lower(), re.UNICODE))
        content_words = set(re.findall(r'\b[\u0600-\u06FF\w]+\b', content.lower(), re.UNICODE))
        
        if not query_words:
            return 0.0
        
        # حساب نسبة التقاطع
        intersection = query_words & content_words
        relevance = len(intersection) / len(query_words)
        
        # معامل إضافي إذا كانت الكلمات متجاورة
        if len(intersection) > 0:
            relevance *= 1.5
        
        return min(relevance, 1.0)
    
    def get_section_info(self, section_name: str) -> Optional[Dict]:
        """الحصول على معلومات قسم معين"""
        # البحث الدقيق
        for section_title in self.knowledge.keys():
            if section_name.lower() in section_title.lower() or section_title.lower() in section_name.lower():
                return {
                    'title': section_title,
                    'content': self.knowledge[section_title]
                }
        return None
    
    def get_answer(self, question: str) -> str:
        """الحصول على إجابة من قاعدة المعرفة"""
        # البحث عن أفضل نتائج
        results = self.search(question, max_results=2)
        
        if not results:
            return "عذراً، لم أجد معلومات مباشرة حول هذا الموضوع. هل يمكنك إعادة صياغة السؤال؟"
        
        # بناء الإجابة من أفضل نتيجة
        best_result = results[0]
        answer = f"**{best_result['section']}**\n\n"
        
        # استخراج الجزء الأكثر صلة
        content = best_result['full_content']
        
        # البحث عن الجمل الأكثر صلة
        sentences = re.split(r'[.!?]\s+', content)
        relevant_sentences = []
        query_words = set(re.findall(r'\b[\u0600-\u06FF\w]+\b', question.lower(), re.UNICODE))
        
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b[\u0600-\u06FF\w]+\b', sentence.lower(), re.UNICODE))
            if len(query_words & sentence_words) > 0:
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            answer += ' '.join(relevant_sentences[:3])  # أول 3 جمل
        else:
            answer += content[:400]  # أول 400 حرف
        
        # إضافة رابط للمزيد
        if len(best_result['full_content']) > 400:
            answer += "\n\n**للمزيد من المعلومات:** يمكنك الاطلاع على القسم الكامل في الدليل الشامل."
        
        return answer
    
    def get_all_sections(self) -> List[str]:
        """الحصول على قائمة بجميع الأقسام"""
        return list(self.knowledge.keys())
    
    def get_quick_info(self, topic: str) -> Optional[str]:
        """الحصول على معلومات سريعة حول موضوع"""
        # البحث في الفهرس
        topic_lower = topic.lower()
        
        # محاولة مطابقة مباشرة
        for section_title, data in self.knowledge.items():
            if topic_lower in section_title.lower():
                # استخراج أول فقرة مفيدة
                content = data['content']
                # البحث عن أول تعريف أو شرح
                match = re.search(r'[-*]\s+\*\*(.+?)\*\*:\s*(.+?)(?=\n[-*]|\n\n|\Z)', content, re.DOTALL)
                if match:
                    return f"**{match.group(1)}:** {match.group(2).strip()[:200]}"
                # أو إرجاع أول 200 حرف
                return content[:200]
        
        return None

# إنشاء نسخة عامة
_global_kb = None

def get_knowledge_base() -> AIKnowledgeBase:
    """الحصول على نسخة عامة من قاعدة المعرفة"""
    global _global_kb
    if _global_kb is None:
        _global_kb = AIKnowledgeBase()
    return _global_kb

