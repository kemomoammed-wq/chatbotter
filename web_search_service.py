# web_search_service.py: خدمة البحث في الإنترنت - يستمد البيانات من الإنترنت مباشرة
"""
خدمة البحث في الإنترنت - يستمد البيانات من الإنترنت مباشرة
بدون الاعتماد على البيانات الثابتة
"""

import logging
import requests
from typing import List, Dict, Optional
from urllib.parse import quote
import time

logger = logging.getLogger(__name__)

class WebSearchService:
    """خدمة البحث في الإنترنت - يستمد البيانات من الإنترنت مباشرة"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 10
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """البحث في DuckDuckGo"""
        try:
            try:
                # الحزمة أعادت التسمية إلى ddgs
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', ''),
                        'source': 'duckduckgo'
                    })
                return results
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            return []
    
    def search_google_custom(self, query: str, max_results: int = 5) -> List[Dict]:
        """البحث في Google (بدون API key - للاستخدام التعليمي)"""
        try:
            # استخدام DuckDuckGo كبديل
            return self.search_duckduckgo(query, max_results)
        except Exception as e:
            logger.warning(f"Google search failed: {e}")
            return []
    
    def search_pharmacy_sites(self, query: str, max_results: int = 5) -> List[Dict]:
        """البحث في مواقع الصيدليات والأدوية"""
        results = []
        try:
            from pharmacy_sites_config import get_search_urls, PHARMACY_KEYWORDS
            
            # إضافة كلمات مفتاحية للبحث إذا كانت مفقودة
            enhanced_query = query
            if not any(kw in query.lower() for kw in PHARMACY_KEYWORDS):
                enhanced_query = f"{query} دواء"
            
            # الحصول على روابط البحث
            search_urls = get_search_urls(enhanced_query)
            
            for site_info in search_urls[:3]:  # أول 3 مواقع
                try:
                    url = site_info['url']
                    # البحث في الموقع
                    response = self.session.get(url, timeout=self.timeout)
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # استخراج النتائج
                        from pharmacy_sites_config import PHARMACY_SITES
                        site_config = PHARMACY_SITES.get(site_info['site'], {})
                        product_selectors = site_config.get('product_selectors', ['.product', '.item'])
                        
                        for selector in product_selectors:
                            products = soup.select(selector)
                            for product in products[:max_results]:
                                title_elem = product.select_one(site_config.get('title_selectors', ['h2', '.title'])[0] if site_config.get('title_selectors') else 'h2')
                                title = title_elem.get_text(strip=True) if title_elem else ''
                                
                                if title:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'snippet': product.get_text(strip=True)[:200],
                                        'source': 'pharmacy_site',
                                        'site_name': site_info['name'],
                                        'country': site_info.get('country', ''),
                                    })
                                    if len(results) >= max_results:
                                        break
                            if len(results) >= max_results:
                                break
                except Exception as e:
                    logger.debug(f"Error searching pharmacy site {site_info['name']}: {e}")
                    continue
        except Exception as e:
            logger.debug(f"Pharmacy sites search error: {e}")
        
        return results[:max_results]
    
    def search_web(self, query: str, max_results: int = 5, language: str = 'ar') -> List[Dict]:
        """البحث في الإنترنت - يجرب عدة مصادر"""
        results = []
        
        # 1. البحث في مواقع الصيدليات أولاً (إذا كان الاستعلام متعلق بالأدوية)
        try:
            from pharmacy_sites_config import PHARMACY_KEYWORDS
            if any(kw in query.lower() for kw in PHARMACY_KEYWORDS):
                pharmacy_results = self.search_pharmacy_sites(query, max_results=3)
                results.extend(pharmacy_results)
                logger.info(f"Found {len(pharmacy_results)} results from pharmacy sites")
        except Exception as e:
            logger.debug(f"Pharmacy search error: {e}")
        
        # 2. البحث في DuckDuckGo
        try:
            ddg_results = self.search_duckduckgo(query, max_results)
            results.extend(ddg_results)
        except Exception as e:
            logger.debug(f"DuckDuckGo search error: {e}")
        
        # 3. إذا لم توجد نتائج كافية، جرب مصادر أخرى
        if len(results) < max_results:
            try:
                # يمكن إضافة مصادر أخرى هنا
                pass
            except Exception as e:
                logger.debug(f"Additional search error: {e}")
        
        return results[:max_results]
    
    def search_and_scrape(self, query: str, max_results: int = 3) -> List[Dict]:
        """البحث في الإنترنت واستخراج البيانات من النتائج"""
        try:
            from web_scraper import get_web_scraper
            
            # البحث أولاً
            search_results = self.search_web(query, max_results=max_results)
            
            if not search_results:
                return []
            
            # استخراج البيانات من النتائج
            scraper = get_web_scraper()
            scraped_data = []
            
            for result in search_results:
                url = result.get('url', '')
                if not url:
                    continue
                
                try:
                    # استخراج البيانات من الرابط
                    scraped = scraper.scrape_url(url, force_refresh=False)
                    if scraped.get('success'):
                        scraped_data.append({
                            'title': scraped.get('title', result.get('title', '')),
                            'url': url,
                            'content': scraped.get('content', result.get('snippet', '')),
                            'description': scraped.get('description', result.get('snippet', '')),
                            'source': 'web_search'
                        })
                except Exception as e:
                    logger.debug(f"Failed to scrape {url}: {e}")
                    # استخدام snippet كبديل
                    scraped_data.append({
                        'title': result.get('title', ''),
                        'url': url,
                        'content': result.get('snippet', ''),
                        'description': result.get('snippet', ''),
                        'source': 'web_search_snippet'
                    })
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"Search and scrape error: {e}")
            return []

# Singleton instance
_web_search_service = None

def get_web_search_service() -> WebSearchService:
    """الحصول على instance موحد من WebSearchService"""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service

