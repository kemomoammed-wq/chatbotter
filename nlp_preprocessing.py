# nlp_preprocessing.py: Optimized NLP pipeline with caching, multilingual support, and language detection
import re
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Optional imports with fallback
NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk import pos_tag
    NLTK_AVAILABLE = True
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        pass
except ImportError:
    logger.warning("NLTK not available - some NLP features will be limited")

SPACY_AVAILABLE = False
try:
    import spacy
    nlp_en = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except:
    logger.warning("spaCy not available - some NLP features will be limited")
    nlp_en = None

SENTIMENT_AVAILABLE = False
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    SENTIMENT_AVAILABLE = True
except:
    logger.warning("vaderSentiment not available - sentiment analysis will be limited")
    analyzer = None

CAMEL_TOOLS_AVAILABLE = False
try:
    from camel_tools.utils.normalize import normalize_alef_maksura_ar, normalize_alef_ar, normalize_teh_marbuta_ar
    from camel_tools.utils.dediac import dediac_ar
    from camel_tools.tokenizers.word import simple_word_tokenize
    CAMEL_TOOLS_AVAILABLE = True
except:
    logger.warning("camel_tools not available - Arabic processing will be limited")

try:
    import numpy as np
except:
    np = None

try:
    from langdetect import detect
except:
    detect = None

# Ensure typing imports are available
from typing import Dict, List, Optional, Any

def clean_text(text: str) -> str:
    """Clean text by removing special characters and extra spaces."""
    try:
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logger.error(f"Error in clean_text: {e}")
        return text

def normalize_arabic(text: str) -> str:
    """Normalize Arabic text for consistency."""
    if not CAMEL_TOOLS_AVAILABLE:
        return text
    try:
        text = normalize_alef_maksura_ar(text)
        text = normalize_alef_ar(text)
        text = normalize_teh_marbuta_ar(text)
        text = dediac_ar(text)
        return text
    except Exception as e:
        logger.error(f"Error in normalize_arabic: {e}")
        return text

def tokenize(text: str, lang: str = 'en') -> List[str]:
    """Tokenize text based on language."""
    try:
        if lang == 'ar':
            if CAMEL_TOOLS_AVAILABLE:
                return simple_word_tokenize(text)
            # Fallback: simple split
            return text.split()
        
        if NLTK_AVAILABLE:
            return nltk.word_tokenize(text)
        # Fallback: simple split
        return text.split()
    except Exception as e:
        logger.error(f"Error in tokenize: {e}")
        return text.split()

def remove_stopwords(tokens: List[str], lang: str = 'en') -> List[str]:
    """Remove stopwords based on language."""
    if not NLTK_AVAILABLE:
        return tokens
    try:
        stops = set(stopwords.words('english' if lang == 'en' else 'arabic'))
        return [t for t in tokens if t not in stops]
    except Exception as e:
        logger.error(f"Error in remove_stopwords: {e}")
        return tokens

def lemmatize(tokens: List[str]) -> List[str]:
    """Lemmatize tokens for better NLP analysis."""
    if not NLTK_AVAILABLE:
        return tokens
    try:
        lemmatizer = WordNetLemmatizer()
        pos = pos_tag(tokens)
        return [lemmatizer.lemmatize(t, pos=p[1][0].lower() if p[1][0].lower() in ['a', 'n', 'v'] else 'n') for t, p in zip(tokens, pos)]
    except Exception as e:
        logger.error(f"Error in lemmatize: {e}")
        return tokens

def extract_entities(text: str, lang: str = 'en') -> List[tuple]:
    """Extract named entities from text."""
    if not SPACY_AVAILABLE or nlp_en is None:
        return []
    try:
        doc = nlp_en(text) if lang == 'en' else nlp_en(text)  # Placeholder for Arabic NER
        return [(ent.text, ent.label_) for ent in doc.ents]
    except Exception as e:
        logger.error(f"Error in extract_entities: {e}")
        return []

def extract_keywords(tokens: List[str], top_n: int = 5) -> List[str]:
    """Extract top keywords based on frequency."""
    if not tokens:
        return []
    if np is None:
        # Fallback: simple frequency counting
        from collections import Counter
        counter = Counter(tokens)
        return [word for word, _ in counter.most_common(top_n)]
    try:
        freq, counts = np.unique(tokens, return_counts=True)
        sorted_idx = np.argsort(counts)[::-1]
        return freq[sorted_idx][:top_n].tolist()
    except Exception as e:
        logger.error(f"Error in extract_keywords: {e}")
        from collections import Counter
        counter = Counter(tokens)
        return [word for word, _ in counter.most_common(top_n)]

def analyze_sentiment(text: str) -> tuple:
    """Analyze sentiment of the text."""
    if not SENTIMENT_AVAILABLE or analyzer is None:
        # Fallback: simple keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'like', 'best', 'perfect', 'جيد', 'رائع', 'ممتاز', 'سعيد', 'أحب']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'sad', 'سيء', 'فظيع', 'أكره', 'حزين']
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        if pos_count > neg_count:
            return 0.5, 'positive'
        elif neg_count > pos_count:
            return -0.5, 'negative'
        return 0, 'neutral'
    
    try:
        scores = analyzer.polarity_scores(text)
        sentiment = 'positive' if scores['compound'] > 0 else 'negative' if scores['compound'] < 0 else 'neutral'
        return scores['compound'], sentiment
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {e}")
        return 0, 'neutral'

def detect_language(text: str) -> str:
    """Detect the language of the input text."""
    if detect is None:
        # Fallback: simple Arabic character detection
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        if arabic_chars > len(text) * 0.3:
            return 'ar'
        return 'en'
    
    try:
        return detect(text)
    except Exception as e:
        logger.error(f"Error in detect_language: {e}")
        # Fallback: simple Arabic character detection
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        if arabic_chars > len(text) * 0.3:
            return 'ar'
        return 'en'

def preprocess_pipeline(text: str, lang: Optional[str] = None) -> Dict[str, Any]:
    """Process text through the full NLP pipeline."""
    try:
        if lang is None:
            lang = detect_language(text)
        cleaned_text = clean_text(text)
        if lang == 'ar':
            cleaned_text = normalize_arabic(cleaned_text)
        tokens = tokenize(cleaned_text, lang)
        tokens = remove_stopwords(tokens, lang)
        tokens = lemmatize(tokens)
        entities = extract_entities(cleaned_text, lang)
        keywords = extract_keywords(tokens)
        sentiment_score, sentiment = analyze_sentiment(cleaned_text)
        return {
            'cleaned_text': cleaned_text,
            'tokens': tokens,
            'entities': entities,
            'keywords': keywords,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'detected_lang': lang
        }
    except Exception as e:
        logger.error(f"Error in preprocess_pipeline: {e}")
        return {
            'cleaned_text': text,
            'tokens': [],
            'entities': [],
            'keywords': [],
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'detected_lang': 'en'
        }