# web_scraper.py: استخراج البيانات من الروابط والمواقع
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse, urljoin
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """فئة لاستخراج البيانات من المواقع والروابط"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.timeout = 15
        # إعدادات خاصة لكل موقع - مع إضافة مواقع الصيدليات
        try:
            from pharmacy_sites_config import PHARMACY_SITES, get_pharmacy_site_config
            self.pharmacy_configs = PHARMACY_SITES
            self.get_pharmacy_config = get_pharmacy_site_config
        except:
            self.pharmacy_configs = {}
            self.get_pharmacy_config = lambda x: {}
        
        self.site_configs = {
            'webteb.com': {
                'content_selectors': ['article', '.content', '.main-content', '.post-content'],
                'title_selectors': ['h1', '.title', '.post-title'],
                'description_selectors': ['.description', '.excerpt', 'meta[name="description"]']
            },
            'wikipedia.org': {
                'content_selectors': ['#mw-content-text', '.mw-parser-output', 'article'],
                'title_selectors': ['h1.firstHeading', '#firstHeading'],
                'description_selectors': ['p:first-of-type', '.mw-parser-output > p']
            },
            'mayoclinic.org': {
                'content_selectors': ['article', '.content', '.article-body'],
                'title_selectors': ['h1', '.article-title'],
                'description_selectors': ['.article-summary', 'meta[name="description"]']
            },
            'healthline.com': {
                'content_selectors': ['article', '.article-body', '.css-0'],
                'title_selectors': ['h1', '.article-title'],
                'description_selectors': ['.article-summary', 'meta[name="description"]']
            },
            # إضافة مواقع الصيدليات
            'sehetak.com': {
                'content_selectors': ['.product-details', '.product-info', 'article', '.content'],
                'title_selectors': ['.product-title', 'h1', 'h2', '.title'],
                'description_selectors': ['.product-description', '.description', 'meta[name="description"]'],
                'price_selectors': ['.price', '.product-price', '.cost']
            },
            'dawaey.com': {
                'content_selectors': ['.content', 'article', '.product-details'],
                'title_selectors': ['.title', 'h1', 'h2'],
                'description_selectors': ['.description', 'meta[name="description"]'],
                'price_selectors': ['.price', '.cost']
            },
            'altibbi.com': {
                'content_selectors': ['article', '.content', '.main-content'],
                'title_selectors': ['h1', '.title', '.article-title'],
                'description_selectors': ['.description', 'meta[name="description"]']
            },
            'nahdionline.com': {
                'content_selectors': ['.product-details', '.product-info', 'article'],
                'title_selectors': ['.product-title', 'h1', 'h2'],
                'description_selectors': ['.product-description', '.description'],
                'price_selectors': ['.price', '.product-price']
            },
        }
    
    def extract_urls(self, text: str) -> List[str]:
        """استخراج جميع الروابط من النص"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _get_site_config(self, url: str) -> Dict:
        """الحصول على إعدادات الموقع المحدد"""
        domain = urlparse(url).netloc.lower()
        for site, config in self.site_configs.items():
            if site in domain:
                return config
        return {}
    
    def scrape_url(self, url: str, force_refresh: bool = False) -> Dict[str, any]:
        """استخراج البيانات من رابط معين"""
        try:
            logger.info(f"جارٍ استخراج البيانات من: {url}")
            start_time = time.time()
            
            # التحقق من وجود البيانات في الكاش (اختياري)
            if not force_refresh:
                from database import get_scraped_data
                cached_data = get_scraped_data(url=url, limit=1)
                if cached_data:
                    # التحقق من عمر البيانات (أقل من 24 ساعة)
                    import datetime
                    cached_time = datetime.datetime.fromisoformat(cached_data[0]['timestamp'])
                    age_hours = (datetime.datetime.now() - cached_time).total_seconds() / 3600
                    if age_hours < 24:
                        logger.info(f"استخدام البيانات المخزنة (عمرها {age_hours:.1f} ساعة)")
                        return {
                            'success': True,
                            'url': url,
                            'title': cached_data[0]['title'],
                            'description': cached_data[0]['description'],
                            'content': cached_data[0]['content'],
                            'source': cached_data[0]['source'],
                            'cached': True,
                            'age_hours': age_hours
                        }
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            # التحقق من نوع المحتوى
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                return {
                    'success': False,
                    'error': f'نوع المحتوى غير مدعوم: {content_type}',
                    'url': url
                }
            
            # تحديد الترميز - تحسين معالجة العربية
            encoding = response.encoding
            if not encoding or encoding == 'ISO-8859-1':
                # محاولة اكتشاف الترميز من المحتوى
                try:
                    import chardet
                    detected = chardet.detect(response.content)
                    encoding = detected.get('encoding', 'utf-8')
                except:
                    encoding = 'utf-8'
            
            # محاولة UTF-8 أولاً للعربية
            try:
                content_str = response.content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content_str = response.content.decode(encoding)
                except:
                    # آخر محاولة - تجاهل الأخطاء
                    content_str = response.content.decode('utf-8', errors='replace')
            
            # استخدام BeautifulSoup مع معالجة أفضل للأخطاء
            soup = BeautifulSoup(content_str, 'html.parser')
            
            # الحصول على إعدادات الموقع
            site_config = self._get_site_config(url)
            
            # استخراج البيانات الأساسية
            title = self._extract_title(soup, site_config)
            description = self._extract_description(soup, site_config)
            content = self._extract_content(soup, site_config)
            images = self._extract_images(soup, url)
            links = self._extract_links(soup, url)
            
            # استخراج بيانات إضافية
            keywords = self._extract_keywords(soup)
            author = self._extract_author(soup)
            publish_date = self._extract_publish_date(soup)
            
            # معالجة خاصة لكل موقع
            result = {
                'success': True,
                'url': url,
                'title': title,
                'description': description,
                'content': content,
                'images': images,
                'links': links,
                'keywords': keywords,
                'author': author,
                'publish_date': publish_date,
                'processing_time': time.time() - start_time
            }
            
            # استخراج السعر إذا كان موقع صيدلية
            site_config = self._get_site_config(url)
            if site_config.get('is_pharmacy') or site_config.get('price_selectors'):
                price = self._extract_price(soup, site_config)
                if price:
                    result['price'] = price
                    result['has_price'] = True
            
            # معالجة خاصة لموقع ويب طب
            if 'webteb.com' in url:
                webteb_data = self._extract_webteb_data(soup, url)
                result['webteb_data'] = webteb_data
                result['source'] = 'webteb'
            elif 'wikipedia.org' in url:
                wiki_data = self._extract_wikipedia_data(soup, url)
                result['wikipedia_data'] = wiki_data
                result['source'] = 'wikipedia'
            else:
                result['source'] = self._detect_source(url)
                
            # إضافة معلومات إضافية لمواقع الصيدليات
            if site_config.get('is_pharmacy'):
                result['site_name'] = site_config.get('site_name', '')
                result['country'] = site_config.get('country', '')
                result['is_pharmacy'] = True
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"انتهت مهلة الاتصال: {url}")
            return {
                'success': False,
                'error': 'انتهت مهلة الاتصال',
                'url': url
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في الاتصال: {url} - {e}")
            return {
                'success': False,
                'error': f'خطأ في الاتصال: {str(e)}',
                'url': url
            }
        except Exception as e:
            logger.error(f"خطأ غير متوقع: {url} - {e}")
            return {
                'success': False,
                'error': f'خطأ غير متوقع: {str(e)}',
                'url': url
            }
    
    def _detect_source(self, url: str) -> str:
        """اكتشاف نوع المصدر من الرابط"""
        domain = urlparse(url).netloc.lower()
        
        # التحقق من مواقع الصيدليات
        try:
            from pharmacy_sites_config import is_pharmacy_site, get_pharmacy_site_config
            if is_pharmacy_site(url):
                config = get_pharmacy_site_config(domain)
                return config.get('name', 'pharmacy') if config else 'pharmacy'
        except:
            pass
        
        if 'webteb' in domain:
            return 'webteb'
        elif 'wikipedia' in domain:
            return 'wikipedia'
        elif 'mayoclinic' in domain:
            return 'mayoclinic'
        elif 'healthline' in domain:
            return 'healthline'
        elif 'sehetak' in domain or 'dawaey' in domain or 'pharmacy' in domain:
            return 'pharmacy'
        elif 'altibbi' in domain:
            return 'altibbi'
        elif 'nahdi' in domain:
            return 'nahdi'
        elif 'medical' in domain or 'health' in domain:
            return 'medical'
        elif 'news' in domain:
            return 'news'
        else:
            return 'general'
    
    def _extract_title(self, soup: BeautifulSoup, site_config: Dict = None) -> str:
        """استخراج العنوان"""
        title = None
        
        # استخدام selectors محددة من إعدادات الموقع
        if site_config and 'title_selectors' in site_config:
            for selector in site_config['title_selectors']:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title:
                        break
        
        # 1. من meta tag og:title
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title.get('content')
        
        # 2. من title tag
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
        
        # 3. من h1
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
        
        # تنظيف العنوان
        if title:
            title = re.sub(r'\s+', ' ', title).strip()
            # إزالة معلومات إضافية شائعة
            title = re.sub(r'\s*[-|]\s*.*$', '', title)
        
        return title or 'بدون عنوان'
    
    def _extract_description(self, soup: BeautifulSoup, site_config: Dict = None) -> str:
        """استخراج الوصف"""
        description = None
        
        # استخدام selectors محددة من إعدادات الموقع
        if site_config and 'description_selectors' in site_config:
            for selector in site_config['description_selectors']:
                if selector.startswith('meta'):
                    # معالجة meta tags
                    if 'name="description"' in selector:
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc and meta_desc.get('content'):
                            description = meta_desc.get('content')
                            break
                else:
                    element = soup.select_one(selector)
                    if element:
                        desc_text = element.get_text(strip=True)
                        if desc_text and len(desc_text) > 50:
                            description = desc_text[:500]  # أول 500 حرف
                            break
        
        # 1. من meta description
        if not description:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc.get('content')
        
        # 2. من og:description
        if not description:
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                description = og_desc.get('content')
        
        # 3. من أول فقرة
        if not description:
            first_p = soup.find('p')
            if first_p:
                desc_text = first_p.get_text(strip=True)
                if desc_text and len(desc_text) > 50:
                    description = desc_text[:500]
        
        return description or ''
    
    def _extract_content(self, soup: BeautifulSoup, site_config: Dict = None) -> str:
        """استخراج المحتوى الرئيسي"""
        # إزالة scripts و styles
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # محاولة العثور على المحتوى الرئيسي
        main_content = None
        
        # استخدام selectors محددة من إعدادات الموقع أولاً
        if site_config and 'content_selectors' in site_config:
            for selector in site_config['content_selectors']:
                elements = soup.select(selector)
                if elements:
                    # اختيار العنصر الأطول
                    main_content = max(elements, key=lambda x: len(x.get_text()))
                    if main_content and len(main_content.get_text()) > 200:
                        break
        
        # البحث عن main, article, أو div.main-content
        if not main_content:
            for tag in ['main', 'article', 'div']:
                elements = soup.find_all(tag, class_=re.compile(r'main|content|article|post|body|text', re.I))
                if elements:
                    # اختيار العنصر الأطول (عادة هو المحتوى الرئيسي)
                    main_content = max(elements, key=lambda x: len(x.get_text()))
                    if main_content and len(main_content.get_text()) > 200:
                        break
        
        if not main_content:
            # استخدام body كبديل
            main_content = soup.find('body')
        
        if main_content:
            # استخراج النص من جميع الفقرات والعناوين
            paragraphs = []
            
            # استخراج العناوين
            for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = heading.get_text(strip=True)
                if heading_text:
                    paragraphs.append(f"\n{heading_text}\n")
            
            # استخراج الفقرات
            for p in main_content.find_all('p'):
                p_text = p.get_text(strip=True)
                if p_text and len(p_text) > 20:  # تجاهل الفقرات القصيرة جداً
                    paragraphs.append(p_text)
            
            # استخراج النص العام إذا لم نجد فقرات
            if not paragraphs:
                text = main_content.get_text(separator='\n', strip=True)
                lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]
                paragraphs = lines
            
            # دمج النص
            full_text = '\n'.join(paragraphs)
            
            # تنظيف النص
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)  # إزالة الأسطر الفارغة المتعددة
            
            # إرجاع النص الكامل (حتى 5000 حرف للبحث، وأول 1000 للعرض)
            return full_text[:5000] if len(full_text) > 5000 else full_text
        
        return ''
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """استخراج الصور"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            if src:
                # تحويل الروابط النسبية إلى مطلقة
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(base_url, src)
                elif not src.startswith('http'):
                    src = urljoin(base_url, src)
                images.append(src)
        return images[:10]  # أول 10 صور
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """استخراج الروابط"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            text = a.get_text(strip=True)
            if href:
                # تحويل الروابط النسبية إلى مطلقة
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    href = urljoin(base_url, href)
                links.append({'url': href, 'text': text[:100]})
        return links[:20]  # أول 20 رابط
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """استخراج الكلمات المفتاحية"""
        keywords = []
        
        # من meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend([k.strip() for k in meta_keywords.get('content').split(',')])
        
        # من meta property keywords
        og_keywords = soup.find('meta', property='article:tag')
        if og_keywords and og_keywords.get('content'):
            keywords.append(og_keywords.get('content'))
        
        return keywords[:10]  # أول 10 كلمات مفتاحية
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """استخراج اسم المؤلف"""
        author = None
        
        # من meta author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            author = meta_author.get('content')
        
        # من meta property author
        if not author:
            og_author = soup.find('meta', property='article:author')
            if og_author and og_author.get('content'):
                author = og_author.get('content')
        
        # من rel="author"
        if not author:
            author_link = soup.find('a', rel='author')
            if author_link:
                author = author_link.get_text(strip=True)
        
        return author or ''
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """استخراج تاريخ النشر"""
        publish_date = None
        
        # من meta property published_time
        meta_date = soup.find('meta', property='article:published_time')
        if meta_date and meta_date.get('content'):
            publish_date = meta_date.get('content')
        
        # من meta name date
        if not publish_date:
            meta_date = soup.find('meta', attrs={'name': 'date'})
            if meta_date and meta_date.get('content'):
                publish_date = meta_date.get('content')
        
        # من time tag
        if not publish_date:
            time_tag = soup.find('time')
            if time_tag:
                publish_date = time_tag.get('datetime') or time_tag.get_text(strip=True)
        
        return publish_date or ''
    
    def _extract_wikipedia_data(self, soup: BeautifulSoup, url: str) -> Dict[str, any]:
        """استخراج بيانات خاصة من ويكيبيديا"""
        wiki_data = {
            'infobox': {},
            'categories': [],
            'references': [],
            'sections': []
        }
        
        try:
            # استخراج infobox
            infobox = soup.find('table', class_='infobox')
            if infobox:
                for row in infobox.find_all('tr'):
                    header = row.find('th')
                    data = row.find('td')
                    if header and data:
                        key = header.get_text(strip=True)
                        value = data.get_text(strip=True)
                        wiki_data['infobox'][key] = value
            
            # استخراج التصنيفات
            categories = soup.find('div', id='catlinks')
            if categories:
                for link in categories.find_all('a'):
                    cat_text = link.get_text(strip=True)
                    if cat_text and cat_text != 'تصنيف':
                        wiki_data['categories'].append(cat_text)
            
            # استخراج الأقسام
            content = soup.find('div', id='mw-content-text')
            if content:
                for heading in content.find_all(['h2', 'h3']):
                    section_title = heading.get_text(strip=True)
                    if section_title:
                        wiki_data['sections'].append(section_title)
            
        except Exception as e:
            logger.error(f"خطأ في استخراج بيانات ويكيبيديا: {e}")
        
        return wiki_data
    
    def _extract_webteb_data(self, soup: BeautifulSoup, url: str) -> Dict[str, any]:
        """استخراج بيانات خاصة من موقع ويب طب"""
        webteb_data = {
            'drug_name': None,
            'drug_info': {},
            'sections': [],
            'common_drugs': [],
            'diseases': []
        }
        
        try:
            # استخراج اسم الدواء من العنوان أو h1
            title = soup.find('h1')
            if title:
                webteb_data['drug_name'] = title.get_text(strip=True)
            
            # البحث عن معلومات الدواء
            # البحث في divs التي تحتوي على معلومات الدواء
            info_sections = soup.find_all(['div', 'section'], class_=re.compile(r'info|details|content|drug', re.I))
            
            for section in info_sections:
                section_text = section.get_text(strip=True)
                if section_text and len(section_text) > 50:
                    webteb_data['sections'].append(section_text[:500])
            
            # البحث عن قائمة الأدوية الشائعة
            common_drugs_section = soup.find_all(['ul', 'ol'], class_=re.compile(r'drug|common|list', re.I))
            for ul in common_drugs_section:
                for li in ul.find_all('li')[:10]:
                    drug_text = li.get_text(strip=True)
                    if drug_text:
                        webteb_data['common_drugs'].append(drug_text)
            
            # البحث عن قائمة الأمراض
            diseases_section = soup.find_all(['ul', 'ol'], class_=re.compile(r'disease|condition|illness', re.I))
            for ul in diseases_section:
                for li in ul.find_all('li')[:10]:
                    disease_text = li.get_text(strip=True)
                    if disease_text:
                        webteb_data['diseases'].append(disease_text)
            
            # استخراج معلومات إضافية من الجداول
            tables = soup.find_all('table')
            for table in tables[:3]:  # أول 3 جداول
                table_data = []
                rows = table.find_all('tr')
                for row in rows[:10]:  # أول 10 صفوف
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        table_data.append(row_data)
                if table_data:
                    webteb_data['drug_info'][f'table_{len(webteb_data["drug_info"])}'] = table_data
            
        except Exception as e:
            logger.error(f"خطأ في استخراج بيانات ويب طب: {e}")
        
        return webteb_data
    
    def _extract_price(self, soup: BeautifulSoup, site_config: Dict = None) -> Optional[str]:
        """استخراج السعر من صفحات المنتجات"""
        price = None
        
        # استخدام selectors محددة من إعدادات الموقع
        if site_config and 'price_selectors' in site_config:
            for selector in site_config['price_selectors']:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    # البحث عن أرقام في النص
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = price_text
                        break
        
        # البحث في meta tags
        if not price:
            price_meta = soup.find('meta', property='product:price:amount')
            if price_meta:
                price = price_meta.get('content', '')
        
        # البحث في schema.org
        if not price:
            price_span = soup.find('span', itemprop='price')
            if price_span:
                price = price_span.get_text(strip=True)
        
        return price
    
    def format_scraped_data(self, data: Dict) -> str:
        """تنسيق البيانات المستخرجة في نص قابل للقراءة"""
        if not data.get('success'):
            return f"❌ فشل استخراج البيانات من {data.get('url', 'الرابط')}: {data.get('error', 'خطأ غير معروف')}"
        
        formatted = f"📄 **البيانات المستخرجة من:** {data['url']}\n\n"
        
        if data.get('title'):
            formatted += f"**العنوان:** {data['title']}\n\n"
        
        if data.get('description'):
            formatted += f"**الوصف:** {data['description']}\n\n"
        
        if data.get('content'):
            content = data['content'][:2000]  # أول 2000 حرف للعرض
            if len(data['content']) > 2000:
                content += "\n\n... (المزيد من المحتوى تم حفظه في قاعدة البيانات)"
            formatted += f"**المحتوى:**\n{content}\n\n"
        
        # بيانات خاصة بويب طب
        if data.get('webteb_data'):
            webteb = data['webteb_data']
            formatted += "**📋 بيانات خاصة بويب طب:**\n\n"
            
            if webteb.get('drug_name'):
                formatted += f"**اسم الدواء:** {webteb['drug_name']}\n\n"
            
            if webteb.get('sections'):
                formatted += "**الأقسام:**\n"
                for i, section in enumerate(webteb['sections'][:3], 1):
                    formatted += f"{i}. {section[:200]}...\n"
                formatted += "\n"
            
            if webteb.get('common_drugs'):
                formatted += f"**أدوية شائعة:** {', '.join(webteb['common_drugs'][:5])}\n\n"
            
            if webteb.get('diseases'):
                formatted += f"**أمراض ذات صلة:** {', '.join(webteb['diseases'][:5])}\n\n"
        
        if data.get('images'):
            formatted += f"**عدد الصور:** {len(data['images'])}\n\n"
        
        if data.get('links'):
            formatted += f"**عدد الروابط:** {len(data['links'])}\n\n"
        
        return formatted

# إنشاء instance عام
_scraper_instance = None

def get_web_scraper() -> WebScraper:
    """الحصول على instance من WebScraper"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = WebScraper()
    return _scraper_instance

