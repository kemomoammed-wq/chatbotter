# pharmacy_sites_config.py: إعدادات مواقع الصيدليات والأدوية العربية
"""
قائمة مواقع الصيدليات والأدوية العربية للبحث وجمع البيانات
"""

PHARMACY_SITES = {
    # مواقع صيدليات مصرية
    'sehetak.com': {
        'name': 'صحتك',
        'country': 'مصر',
        'search_url': 'https://www.sehetak.com/search?q={query}',
        'product_selectors': ['.product-item', '.product-card', '.product'],
        'title_selectors': ['.product-title', 'h2', 'h3'],
        'price_selectors': ['.price', '.product-price', '.cost'],
        'description_selectors': ['.product-description', '.description', 'p'],
        'content_selectors': ['.product-details', '.product-info', 'article'],
    },
    'dawaey.com': {
        'name': 'دواي',
        'country': 'مصر',
        'search_url': 'https://www.dawaey.com/search?q={query}',
        'product_selectors': ['.product', '.item', '.card'],
        'title_selectors': ['.title', 'h2', 'h3'],
        'price_selectors': ['.price', '.cost'],
        'description_selectors': ['.description', 'p'],
        'content_selectors': ['.content', 'article'],
    },
    'pharmacyonline.com.eg': {
        'name': 'صيدلية أونلاين',
        'country': 'مصر',
        'search_url': 'https://www.pharmacyonline.com.eg/search?q={query}',
        'product_selectors': ['.product', '.product-item'],
        'title_selectors': ['.product-name', 'h2'],
        'price_selectors': ['.price', '.product-price'],
        'description_selectors': ['.product-description'],
        'content_selectors': ['.product-details'],
    },
    # مواقع صيدليات سعودية
    'nahdionline.com': {
        'name': 'صيدلية النهدي',
        'country': 'السعودية',
        'search_url': 'https://www.nahdionline.com/ar/search?q={query}',
        'product_selectors': ['.product-item', '.product-card'],
        'title_selectors': ['.product-title', 'h2'],
        'price_selectors': ['.price', '.product-price'],
        'description_selectors': ['.product-description'],
        'content_selectors': ['.product-details'],
    },
    'alnahdi.com': {
        'name': 'النهدي',
        'country': 'السعودية',
        'search_url': 'https://www.alnahdi.com/search?q={query}',
        'product_selectors': ['.product', '.item'],
        'title_selectors': ['.title', 'h2'],
        'price_selectors': ['.price'],
        'description_selectors': ['.description'],
        'content_selectors': ['.content'],
    },
    # مواقع معلومات طبية
    'webteb.com': {
        'name': 'ويب طب',
        'country': 'عربي',
        'search_url': 'https://www.webteb.com/search?q={query}',
        'product_selectors': ['.article', '.post', '.content-item'],
        'title_selectors': ['h1', '.title', '.article-title'],
        'price_selectors': [],
        'description_selectors': ['.description', '.excerpt', 'meta[name="description"]'],
        'content_selectors': ['article', '.content', '.main-content'],
    },
    'altibbi.com': {
        'name': 'الطبي',
        'country': 'عربي',
        'search_url': 'https://www.altibbi.com/search?q={query}',
        'product_selectors': ['.article', '.post'],
        'title_selectors': ['h1', '.title'],
        'price_selectors': [],
        'description_selectors': ['.description', 'meta[name="description"]'],
        'content_selectors': ['article', '.content'],
    },
    'dailymedicalinfo.com': {
        'name': 'معلومات طبية يومية',
        'country': 'مصر',
        'search_url': 'https://www.dailymedicalinfo.com/search?q={query}',
        'product_selectors': ['.post', '.article'],
        'title_selectors': ['h1', '.title'],
        'price_selectors': [],
        'description_selectors': ['.description'],
        'content_selectors': ['article', '.content'],
    },
    # مواقع معلومات أدوية
    'm3lomat.com': {
        'name': 'معلومات',
        'country': 'عربي',
        'search_url': 'https://www.m3lomat.com/search?q={query}',
        'product_selectors': ['.article', '.post'],
        'title_selectors': ['h1', '.title'],
        'price_selectors': [],
        'description_selectors': ['.description'],
        'content_selectors': ['article', '.content'],
    },
    'drugs.com': {
        'name': 'Drugs.com (Arabic)',
        'country': 'عالمي',
        'search_url': 'https://www.drugs.com/search.php?searchterm={query}',
        'product_selectors': ['.search-result', '.drug-item'],
        'title_selectors': ['h2', '.title'],
        'price_selectors': [],
        'description_selectors': ['.description', 'p'],
        'content_selectors': ['.content', 'article'],
    },
}

# كلمات مفتاحية للبحث في مواقع الأدوية
PHARMACY_KEYWORDS = [
    'دواء', 'أدوية', 'صيدلية', 'صيدليات', 'علاج', 'أعراض', 'جرعة',
    'موانع الاستخدام', 'آثار جانبية', 'تفاعلات دوائية',
    'باراسيتامول', 'إيبوبروفين', 'أموكسيسيلين', 'أزيثرومايسين',
    'فيتامين', 'مكمل غذائي', 'مستحضر', 'كريم', 'مرهم', 'قطرة',
    'حبوب', 'كبسولات', 'شراب', 'حقن', 'تحاميل'
]

# مواقع للبحث التلقائي
AUTO_SEARCH_SITES = [
    'webteb.com',
    'altibbi.com',
    'sehetak.com',
    'dawaey.com',
    'nahdionline.com',
]

def get_pharmacy_site_config(domain: str) -> dict:
    """الحصول على إعدادات موقع صيدلية"""
    for site_domain, config in PHARMACY_SITES.items():
        if site_domain in domain.lower():
            return config
    return {}

def is_pharmacy_site(url: str) -> bool:
    """التحقق إذا كان الموقع موقع صيدلية"""
    domain = url.lower()
    return any(site in domain for site in PHARMACY_SITES.keys())

def get_search_urls(query: str, sites: list = None) -> list:
    """الحصول على روابط البحث لمواقع الصيدليات"""
    if sites is None:
        sites = AUTO_SEARCH_SITES
    
    urls = []
    for site_domain in sites:
        if site_domain in PHARMACY_SITES:
            config = PHARMACY_SITES[site_domain]
            search_url = config.get('search_url', '').format(query=query)
            if search_url:
                urls.append({
                    'url': search_url,
                    'site': site_domain,
                    'name': config.get('name', site_domain),
                    'country': config.get('country', ''),
                })
    return urls

