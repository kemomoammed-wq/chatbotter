# add_training_data.py: إضافة بيانات تدريب كثيرة للشات بوت
"""
سكريبت لإضافة بيانات تدريب كثيرة للشات بوت
Script to add extensive training data for the chatbot
"""
import logging
import os
from database import save_scraped_data, save_medical_data, save_conversation, Session, ScrapedData, MedicalData, Conversation

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training_data.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# بيانات تدريب شاملة
TRAINING_DATA = {
    'scraped_data': [
        {
            'url': 'https://eva.com/skincare/acne-treatment',
            'title': 'علاج حب الشباب - إيفا',
            'description': 'دليل شامل لعلاج حب الشباب باستخدام منتجات إيفا',
            'content': '''
            علاج حب الشباب - دليل شامل من إيفا
            
            حب الشباب من المشاكل الجلدية الشائعة التي تؤثر على ملايين الأشخاص حول العالم. في إيفا، نقدم حلولاً فعالة وآمنة لعلاج حب الشباب.
            
            المنتجات الموصى بها:
            1. غسول إيفا اللطيف للبشرة الدهنية (150 ج)
               - يحتوي على حمض الساليسيليك 2%
               - ينظف المسام بعمق
               - يقلل البكتيريا المسببة للحبوب
            
            2. سيرم فيتامين C المضاد للأكسدة (350 ج)
               - يفتح البقع الداكنة
               - يحارب البكتيريا الضارة
               - يعزز إشراقة البشرة
            
            3. كريم علاج الحبوب (280 ج)
               - يحتوي على البنزويل بيروكسايد
               - علاج موضعي فعال
               - يقلل الالتهاب
            
            الروتين الموصى به:
            - صباحاً: غسول → سيرم → مرطب خفيف → واقي شمس
            - مساءً: غسول → علاج موضعي → مرطب مهدئ
            
            نصائح مهمة:
            - لا تعصر الحبوب نهائياً
            - غير غطاء الوسادة يومياً
            - تجنب لمس الوجه
            - النتائج تظهر خلال 4-6 أسابيع
            ''',
            'source': 'medical',
            'metadata': {'category': 'acne', 'priority': 10}
        },
        {
            'url': 'https://eva.com/skincare/dry-skin',
            'title': 'علاج البشرة الجافة - إيفا',
            'description': 'حلول فعالة لترطيب البشرة الجافة',
            'content': '''
            علاج البشرة الجافة - حلول إيفا
            
            البشرة الجافة تحتاج إلى عناية خاصة وترطيب مكثف. منتجات إيفا مصممة خصيصاً للبشرة الجافة.
            
            المنتجات الموصى بها:
            1. مرطب إيفا المائي للبشرة الجافة (220 ج)
               - حمض الهيالورونيك يحتفظ بالرطوبة 48 ساعة
               - نياسيناميد 5% يقوي حاجز البشرة
               - السيراميدز تمنع فقدان الماء
            
            2. مقشر إيفا اللطيف للبشرة الحساسة (180 ج)
               - أحماض فواكه طبيعية
               - الشوفان والعسل يرطبان بعمق
            
            3. سيرم الترطيب المكثف (320 ج)
               - ترطيب فوري وطويل المدى
               - مناسب للبشرة الجافة جداً
            
            الروتين الموصى به:
            - صباحاً: غسول لطيف → سيرم مرطب → مرطب غني → واقي شمس
            - مساءً: زيت منظف → سيرم → كريم ليلي مكثف
            - أسبوعياً: مقشر لطيف مرة واحدة
            
            نصائح مهمة:
            - استخدمي الماء الفاتر (ليس ساخن)
            - رطبي البشرة فوراً بعد الغسيل
            - تجنبي المنتجات القاسية
            - اشربي الكثير من الماء
            ''',
            'source': 'medical',
            'metadata': {'category': 'dry_skin', 'priority': 10}
        },
        {
            'url': 'https://eva.com/haircare/damaged-hair',
            'title': 'علاج الشعر التالف - إيفا',
            'description': 'منتجات إيفا لإصلاح الشعر التالف',
            'content': '''
            علاج الشعر التالف - منتجات إيفا
            
            الشعر التالف يحتاج إلى عناية خاصة وإصلاح مكثف. إيفا تقدم حلولاً فعالة لإصلاح الشعر التالف.
            
            المنتجات الموصى بها:
            1. شامبو ألو إيفا المرطب (120 ج)
               - للشعر الجاف والمتضرر والمعالج كيميائياً
               - ترطيب عميق وإصلاح التلف
               - لمعان طبيعي
            
            2. ماسك إيفا هير كلينك للإصلاح المكثف (200 ج)
               - للشعر التالف والمصبوغ والمتقصف
               - إصلاح عميق وتقوية البصيلات
               - يمنع التقصف
            
            3. بلسم إيفا للشعر الجاف (150 ج)
               - ترطيب فوري وسهولة في التمشيط
               - يحمي من الحرارة
            
            الروتين الموصى به:
            - استخدمي الشامبو والبلسم في كل غسلة
            - استخدمي الماسك مرة أو مرتين أسبوعياً
            - تجنبي الحرارة الزائدة
            - قصي الأطراف بانتظام
            
            نصائح مهمة:
            - استخدمي مشط واسع الأسنان
            - جففي الشعر بالمنشفة برفق
            - تجنبي الصبغة الكيميائية القاسية
            ''',
            'source': 'haircare',
            'metadata': {'category': 'damaged_hair', 'priority': 9}
        },
    ],
    'medical_data': [
        {
            'title': 'فيتامين C للبشرة',
            'content': '''
            فيتامين C من أهم الفيتامينات للبشرة:
            
            الفوائد:
            - يفتح البقع الداكنة
            - يحارب الجذور الحرة
            - يعزز إنتاج الكولاجين
            - يحمي من أشعة الشمس الضارة
            
            منتجات إيفا:
            - سيرم فيتامين C المضاد للأكسدة (350 ج)
            
            طريقة الاستخدام:
            - استخدمي صباحاً بعد الغسيل
            - ضعي قبل المرطب
            - استخدمي واقي شمس بعده
            
            النتائج:
            - تظهر خلال 4-6 أسابيع
            - بشرة أكثر إشراقة
            - بقع أقل وضوحاً
            ''',
            'category': 'vitamins',
            'keywords': 'فيتامين سي، فيتامين c، سيرم، مضاد أكسدة، إشراقة',
            'dosage': 'مرة واحدة يومياً صباحاً',
            'side_effects': 'نادراً ما يسبب تهيج للبشرة الحساسة',
            'contraindications': 'لا يستخدم مع منتجات تحتوي على الريتينول في نفس الوقت'
        },
        {
            'title': 'حمض الهيالورونيك للترطيب',
            'content': '''
            حمض الهيالورونيك من أقوى المرطبات:
            
            الفوائد:
            - يحتفظ بالرطوبة 1000 مرة من وزنه
            - ترطيب فوري وطويل المدى
            - مناسب لجميع أنواع البشرة
            - يقلل التجاعيد الدقيقة
            
            منتجات إيفا:
            - مرطب إيفا المائي (220 ج)
            - سيرم الترطيب المكثف (320 ج)
            
            طريقة الاستخدام:
            - استخدمي صباحاً ومساءً
            - ضعي على البشرة الرطبة
            - اتبعي بالمرطب
            
            النتائج:
            - ترطيب فوري
            - بشرة أكثر نعومة
            - تقليل التجاعيد
            ''',
            'category': 'moisturizers',
            'keywords': 'حمض هيالورونيك، ترطيب، مرطب، مائي، نعومة',
            'dosage': 'مرتين يومياً',
            'side_effects': 'آمن للاستخدام',
            'contraindications': 'لا توجد'
        },
        {
            'title': 'الساليسيليك أسيد لعلاج الحبوب',
            'content': '''
            الساليسيليك أسيد من أفضل المكونات لعلاج حب الشباب:
            
            الفوائد:
            - ينظف المسام بعمق
            - يزيل الخلايا الميتة
            - يقلل الالتهاب
            - يمنع ظهور حبوب جديدة
            
            منتجات إيفا:
            - غسول إيفا اللطيف للبشرة الدهنية (150 ج)
            
            طريقة الاستخدام:
            - استخدمي صباحاً ومساءً
            - رغبي واتركي لمدة 30 ثانية
            - اشطفي بالماء الفاتر
            
            النتائج:
            - تنظيف عميق للمسام
            - تقليل الحبوب
            - بشرة أكثر نظافة
            
            تحذيرات:
            - قد يسبب جفاف في البداية
            - استخدمي مرطب بعده
            - تجنبي التعرض للشمس المباشرة
            ''',
            'category': 'acne_treatment',
            'keywords': 'ساليسيليك، حب شباب، غسول، تنظيف، مسام',
            'dosage': 'مرتين يومياً',
            'side_effects': 'جفاف خفيف في البداية',
            'contraindications': 'البشرة الحساسة جداً'
        },
    ],
    'conversations': [
        {
            'user_id': 'training-1',
            'message': 'عندي حبوب في وجهي',
            'response': 'فهمت إن عندك مشكلة حبوب! 🤗 دي مشكلة شائعة وليها حل:\n\n💄 المنتجات المناسبة:\n• غسول إيفا اللطيف للبشرة الدهنية - 150ج\n• سيرم فيتامين C المضاد للأكسدة - 350ج\n\n🔄 الروتين المثالي:\nصباحاً: غسول → سيرم → مرطب خفيف → واقي شمس\nمساءً: غسول → علاج موضعي → مرطب مهدئ',
            'intent': 'acne_treatment',
            'sentiment': 'neutral',
            'confidence': 0.95
        },
        {
            'user_id': 'training-2',
            'message': 'بشرتي جافة جداً',
            'response': 'أشوف إن بشرتك جافة! 💧 مش مشكلة، إيفا عندها الحل السحري:\n\n💄 المنتجات المناسبة:\n• مرطب إيفا المائي للبشرة الجافة - 220ج\n• مقشر إيفا اللطيف - 180ج\n\n🔄 الروتين السحري:\nصباحاً: غسول لطيف → سيرم مرطب → مرطب غني → واقي شمس\nمساءً: زيت منظف → سيرم → كريم ليلي مكثف',
            'intent': 'dry_skin_treatment',
            'sentiment': 'neutral',
            'confidence': 0.95
        },
        {
            'user_id': 'training-3',
            'message': 'شعري تالف ومتقصف',
            'response': 'أهلاً! 🌟 أنا هنا عشان أساعدك في اختيار منتجات الشعر المناسبة لشعرك:\n\n💇‍♀️ منتجات إيفا المميزة:\n• شامبو ألو إيفا المرطب (كود 101) - 120ج\n• ماسك إيفا هير كلينك للإصلاح المكثف (كود 102) - 200ج\n• بلسم إيفا للشعر الجاف (كود 103) - 150ج',
            'intent': 'haircare',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-4',
            'message': 'محتاج منتج للبشرة',
            'response': 'أهلاً! 🎯 أنا هنا عشان أساعدك في اختيار المنتجات المناسبة لبشرتك:\n\n💄 منتجات إيفا المميزة:\n• غسول إيفا اللطيف للبشرة الدهنية (كود 001) - 150ج\n• مرطب إيفا المائي للبشرة الجافة (كود 002) - 220ج\n• واقي الشمس إيفا SPF 50+ (كود 003) - 280ج\n• سيرم فيتامين C المضاد للأكسدة (كود 004) - 350ج\n\n🔍 عشان أقدر أوصيك بالمنتج المناسب، قولي:\n• نوع بشرتك (دهنية، جافة، عادية، حساسة)\n• المشكلة اللي عندك (حبوب، جفاف، بقع، تجاعيد)',
            'intent': 'product_inquiry',
            'sentiment': 'neutral',
            'confidence': 0.85
        },
        {
            'user_id': 'training-5',
            'message': 'إيه سعر منتجاتكم؟',
            'response': 'أسعار منتجات إيفا:\n\n💄 منتجات العناية بالبشرة:\n• غسول إيفا اللطيف - 150ج\n• مرطب إيفا المائي - 220ج\n• واقي الشمس SPF 50+ - 280ج\n• سيرم فيتامين C - 350ج\n• مقشر إيفا اللطيف - 180ج\n\n💇‍♀️ منتجات العناية بالشعر:\n• شامبو ألو إيفا - 120ج\n• ماسك إيفا هير كلينك - 200ج\n• بلسم إيفا - 150ج\n\n🛍️ عايز تعرف أكتر عن منتج معين؟',
            'intent': 'pricing',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-6',
            'message': 'How to use vitamin C serum?',
            'response': 'Here\'s how to use Vitamin C Serum:\n\n📅 When to use:\n• Morning routine (best time)\n• After cleansing\n• Before moisturizer\n• Always follow with sunscreen\n\n💧 How to apply:\n1. Cleanse your face\n2. Apply 2-3 drops of serum\n3. Gently massage into skin\n4. Wait 2-3 minutes\n5. Apply moisturizer\n6. Apply sunscreen (SPF 50+)\n\n⚠️ Important:\n• Don\'t use with retinol at the same time\n• Start with every other day\n• Results appear in 4-6 weeks\n• Store in a cool, dark place',
            'intent': 'product_usage',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-7',
            'message': 'عندي بقع داكنة في وجهي',
            'response': 'فهمت إن عندك بقع داكنة! 🌟 دي مشكلة شائعة وليها حل:\n\n💄 المنتجات المناسبة:\n• سيرم فيتامين C المضاد للأكسدة - 350ج\n  ▫️ يفتح البقع الداكنة تدريجياً\n  ▫️ يوحد لون البشرة\n  ▫️ يعزز إشراقة البشرة\n\n• مقشر إيفا اللطيف - 180ج\n  ▫️ يزيل الخلايا الميتة\n  ▫️ يفتح البقع تدريجياً\n\n🔄 الروتين الموصى به:\nصباحاً: غسول → سيرم فيتامين C → مرطب → واقي شمس (مهم جداً!)\nمساءً: غسول → مقشر (مرة أسبوعياً) → مرطب\n\n⏱️ النتائج:\n• تظهر خلال 4-6 أسابيع\n• استخدام منتظم مهم جداً\n• واقي الشمس ضروري لمنع ظهور بقع جديدة',
            'intent': 'dark_spots',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-8',
            'message': 'بشرتي دهنية وعندي لمعان',
            'response': 'بشرتك دهنية؟ 🌟 ده مش عيب، ده نعمة لو عرفتِ تتعاملي معاها صح! أنا هنا عشان أساعدك:\n\n💄 المنتجات المناسبة:\n• غسول إيفا اللطيف للبشرة الدهنية - 150ج\n  ▫️ ينظف الزيوت الزائدة بدون جفاف\n  ▫️ حمض الساليسيليك ينظف المسام بعمق\n\n• واقي الشمس إيفا SPF 50+ - 280ج\n  ▫️ تركيبة خفيفة غير دهنية\n  ▫️ مقاوم للماء والعرق\n  ▫️ لا يسد المسام\n\n🔄 الروتين الموصى به:\nصباحاً: غسول → سيرم خفيف → واقي شمس\nمساءً: غسول → مقشر (مرتين أسبوعياً) → مرطب خفيف',
            'intent': 'oily_skin',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-9',
            'message': 'عندي تجاعيد في وجهي',
            'response': 'التجاعيد جزء طبيعي من التقدم في العمر، لكن ممكن نبطئ ظهورها! 💪\n\n💄 المنتجات المناسبة:\n• سيرم فيتامين C المضاد للأكسدة - 350ج\n  ▫️ يحفز إنتاج الكولاجين\n  ▫️ يقلل التجاعيد الدقيقة\n\n• مرطب إيفا المائي - 220ج\n  ▫️ حمض الهيالورونيك يرطب بعمق\n  ▫️ يقلل ظهور التجاعيد\n\n🔄 الروتين الموصى به:\nصباحاً: غسول → سيرم فيتامين C → مرطب → واقي شمس (مهم جداً!)\nمساءً: غسول → سيرم → كريم ليلي مكثف\n\n💡 نصائح مهمة:\n• واقي الشمس أهم منتج ضد التجاعيد\n• النوم الكافي مهم جداً\n• شرب الماء بانتظام',
            'intent': 'anti_aging',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-10',
            'message': 'بشرتي حساسة ومتهيجة',
            'response': 'البشرة الحساسة تحتاج عناية خاصة جداً! 🧡\n\n💄 المنتجات المناسبة:\n• غسول إيفا اللطيف للبشرة الحساسة - 150ج\n  ▫️ خالي من العطور\n  ▫️ لطيف جداً على البشرة\n\n• مرطب إيفا المائي - 220ج\n  ▫️ مهدئ للبشرة الحساسة\n  ▫️ خالي من المكونات المهيجة\n\n🔄 الروتين الموصى به:\nصباحاً: غسول لطيف → مرطب → واقي شمس\nمساءً: غسول لطيف → مرطب مهدئ\n\n⚠️ نصائح مهمة:\n• تجنبي المنتجات القاسية\n• اختبري المنتجات على منطقة صغيرة أولاً\n• استخدمي منتجات خالية من العطور',
            'intent': 'sensitive_skin',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-11',
            'message': 'What products do you have?',
            'response': 'Eva has an amazing range of products! 💄\n\n**Skincare Products:**\n• Eva Gentle Cleanser (code 001) - 150 EGP\n• Eva Hydrating Moisturizer (code 002) - 220 EGP\n• Eva Sunscreen SPF 50+ (code 003) - 280 EGP\n• Vitamin C Antioxidant Serum (code 004) - 350 EGP\n• Eva Gentle Exfoliator (code 005) - 180 EGP\n\n**Haircare Products:**\n• Aloe Eva Hydrating Shampoo (code 101) - 120 EGP\n• Eva Hair Clinic Repair Mask (code 102) - 200 EGP\n• Eva Conditioner (code 103) - 150 EGP\n\n💡 Want to know more about a specific product?',
            'intent': 'product_list',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-12',
            'message': 'How much does the cleanser cost?',
            'response': 'Eva Gentle Cleanser costs **150 EGP** 💰\n\n**Product Details:**\n• For oily and acne-prone skin\n• Contains 2% Salicylic Acid\n• Deep pore cleansing\n• Reduces bacteria\n\n**How to use:**\n• Morning and evening\n• Lather and leave for 30 seconds\n• Rinse with warm water\n\n💡 Want to know about other products?',
            'intent': 'product_price',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-13',
            'message': 'ممكن أعرف عن منتج فيتامين سي؟',
            'response': 'سيرم فيتامين C المضاد للأكسدة - 350ج 💎\n\n**الفوائد:**\n• يفتح البقع الداكنة\n• يحارب الجذور الحرة\n• يعزز إنتاج الكولاجين\n• يحمي من أشعة الشمس الضارة\n• يوحد لون البشرة\n\n**طريقة الاستخدام:**\n• صباحاً بعد الغسيل\n• ضعي 2-3 قطرات\n• اتبعي بالمرطب ثم واقي الشمس\n\n**النتائج:**\n• تظهر خلال 4-6 أسابيع\n• بشرة أكثر إشراقة\n\n💡 عايز تعرف أكتر عن منتج تاني؟',
            'intent': 'product_info',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-14',
            'message': 'إيه أفضل روتين للبشرة الدهنية؟',
            'response': 'روتين مثالي للبشرة الدهنية! ✨\n\n**صباحاً:**\n1. غسول إيفا اللطيف للبشرة الدهنية\n2. سيرم خفيف (اختياري)\n3. واقي الشمس SPF 50+ (مهم جداً!)\n\n**مساءً:**\n1. غسول إيفا اللطيف\n2. مقشر (مرتين أسبوعياً)\n3. مرطب خفيف غير دهني\n\n**أسبوعياً:**\n• مقشر لطيف مرة أو مرتين\n• ماسك للبشرة الدهنية (اختياري)\n\n**نصائح مهمة:**\n• لا تغسلي وجهك أكثر من مرتين يومياً\n• استخدمي منتجات خفيفة غير دهنية\n• واقي الشمس ضروري حتى في الشتاء\n• تجنبي المنتجات الثقيلة\n\n💡 عايز توصيات منتجات محددة؟',
            'intent': 'routine_advice',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-15',
            'message': 'Can I use vitamin C with retinol?',
            'response': 'Great question! Here\'s the answer: ⚠️\n\n**General Rule:**\n• Don\'t use them at the same time\n• They can cause irritation when combined\n\n**Best Practice:**\n• **Morning:** Vitamin C Serum + Sunscreen\n• **Evening:** Retinol (if you use it)\n\n**Why?**\n• Vitamin C works best in the morning (protects from sun)\n• Retinol works best at night (sensitive to light)\n• Separating them reduces irritation risk\n\n**Alternative:**\n• Use Vitamin C daily in the morning\n• Use Retinol 2-3 times per week at night\n\n💡 Want a personalized routine?',
            'intent': 'product_compatibility',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-16',
            'message': 'شعري جاف ومتقصف',
            'response': 'الشعر الجاف والمتقصف يحتاج عناية خاصة! 💇‍♀️\n\n**المنتجات المناسبة:**\n• شامبو ألو إيفا المرطب (120ج)\n  ▫️ ترطيب عميق للشعر الجاف\n  ▫️ إصلاح التلف\n\n• ماسك إيفا هير كلينك (200ج)\n  ▫️ إصلاح مكثف للشعر التالف\n  ▫️ يمنع التقصف\n\n• بلسم إيفا للشعر الجاف (150ج)\n  ▫️ ترطيب فوري\n  ▫️ سهولة في التمشيط\n\n**الروتين الموصى به:**\n• استخدمي الشامبو والبلسم في كل غسلة\n• استخدمي الماسك مرة أو مرتين أسبوعياً\n• قصي الأطراف بانتظام\n• تجنبي الحرارة الزائدة\n\n💡 عايز تعرف أكتر عن منتج معين؟',
            'intent': 'dry_hair',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-17',
            'message': 'إيه الفرق بين الشامبو والبلسم؟',
            'response': 'سؤال مهم! 🤔\n\n**الشامبو:**\n• ينظف الشعر وفروة الرأس\n• يزيل الأوساخ والزيوت الزائدة\n• يستخدم أولاً في كل غسلة\n• مثال: شامبو ألو إيفا المرطب (120ج)\n\n**البلسم:**\n• يرطب الشعر بعد الغسيل\n• يسهل التمشيط\n• يحمي من التلف\n• يستخدم بعد الشامبو\n• مثال: بلسم إيفا للشعر الجاف (150ج)\n\n**الترتيب الصحيح:**\n1. شامبو (ينظف)\n2. بلسم (يرطب)\n3. ماسك (مرة أسبوعياً - إصلاح مكثف)\n\n💡 عايز تعرف أكتر عن منتج معين؟',
            'intent': 'product_difference',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-18',
            'message': 'How often should I exfoliate?',
            'response': 'Great question about exfoliation! 🧴\n\n**General Rule:**\n• **Normal/Oily Skin:** 2-3 times per week\n• **Dry/Sensitive Skin:** Once per week\n• **Combination Skin:** 1-2 times per week\n\n**Eva Gentle Exfoliator (180 EGP):**\n• Natural fruit acids\n• Gentle on skin\n• Removes dead cells\n\n**Signs you\'re over-exfoliating:**\n• Redness\n• Irritation\n• Dryness\n• Sensitivity\n\n**Best Time:**\n• Evening routine\n• After cleansing\n• Before moisturizer\n\n💡 Want product recommendations?',
            'intent': 'exfoliation_advice',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-19',
            'message': 'عندي رؤوس سوداء في أنفي',
            'response': 'الرؤوس السوداء مشكلة شائعة! 🖤\n\n**المنتجات المناسبة:**\n• غسول إيفا اللطيف للبشرة الدهنية (150ج)\n  ▫️ حمض الساليسيليك ينظف المسام\n  ▫️ يزيل الرؤوس السوداء تدريجياً\n\n• مقشر إيفا اللطيف (180ج)\n  ▫️ يزيل الخلايا الميتة\n  ▫️ ينظف المسام\n\n**الروتين الموصى به:**\n• غسول يومياً صباحاً ومساءً\n• مقشر مرة أو مرتين أسبوعياً\n• واقي شمس يومياً\n\n**نصائح مهمة:**\n• لا تعصري الرؤوس السوداء (يسبب التهاب)\n• استخدمي منتجات تنظيف المسام\n• واقي الشمس يمنع ظهور رؤوس سوداء جديدة\n\n💡 عايز تعرف أكتر عن المنتجات؟',
            'intent': 'blackheads',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
        {
            'user_id': 'training-20',
            'message': 'What is SPF and why is it important?',
            'response': 'SPF (Sun Protection Factor) is crucial! ☀️\n\n**What it does:**\n• Protects from UVB rays (burning)\n• Prevents sun damage\n• Reduces risk of skin cancer\n• Prevents premature aging\n• Prevents dark spots\n\n**Eva Sunscreen SPF 50+ (280 EGP):**\n• High protection\n• Lightweight formula\n• Non-greasy\n• Water resistant\n\n**How to use:**\n• Apply every morning\n• Reapply every 2 hours if outside\n• Use even on cloudy days\n• Apply 15 minutes before sun exposure\n\n**Why SPF 50+?**\n• Blocks 98% of UVB rays\n• Best protection for daily use\n\n💡 Want to know more?',
            'intent': 'sunscreen_info',
            'sentiment': 'neutral',
            'confidence': 0.90
        },
    ]
}

def add_training_data():
    """إضافة بيانات التدريب"""
    logger.info("="*60)
    logger.info("🚀 Starting Training Data Addition")
    logger.info("="*60)
    
    session = Session()
    added_count = 0
    
    try:
        # 1. Add scraped data
        logger.info("\n[1/3] Adding scraped data...")
        for data in TRAINING_DATA['scraped_data']:
            try:
                success = save_scraped_data(
                    url=data['url'],
                    title=data['title'],
                    description=data['description'],
                    content=data['content'],
                    source=data['source'],
                    metadata=data.get('metadata', {})
                )
                if success:
                    added_count += 1
                    logger.info(f"✅ Added: {data['title']}")
            except Exception as e:
                logger.error(f"❌ Error adding {data['title']}: {e}")
        
        # 2. Add medical data
        logger.info("\n[2/3] Adding medical data...")
        for data in TRAINING_DATA['medical_data']:
            try:
                success = save_medical_data(
                    title=data['title'],
                    content=data['content'],
                    category=data['category'],
                    keywords=data.get('keywords', ''),
                    dosage=data.get('dosage'),
                    side_effects=data.get('side_effects'),
                    contraindications=data.get('contraindications'),
                    source='training'
                )
                if success:
                    added_count += 1
                    logger.info(f"✅ Added: {data['title']}")
            except Exception as e:
                logger.error(f"❌ Error adding {data['title']}: {e}")
        
        # 3. Add conversations
        logger.info("\n[3/3] Adding conversations...")
        for conv in TRAINING_DATA['conversations']:
            try:
                save_conversation(
                    user_id=conv['user_id'],
                    message=conv['message'],
                    response=conv['response'],
                    intent=conv['intent'],
                    sentiment=conv['sentiment'],
                    confidence=conv['confidence']
                )
                added_count += 1
                logger.info(f"✅ Added conversation: {conv['message'][:50]}...")
            except Exception as e:
                logger.error(f"❌ Error adding conversation: {e}")
        
        logger.info("\n" + "="*60)
        logger.info(f"✅ Successfully added {added_count} training data items!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Error in add_training_data: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    add_training_data()

