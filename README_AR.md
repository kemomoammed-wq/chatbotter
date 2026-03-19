# 🤖 Eva Chatbot - دليل المستخدم الكامل

## 🚀 البدء السريع

### خطوة واحدة فقط!

```bash
START.bat
```

**هذا كل شيء!** 🎉

---

## 📋 الملفات المتاحة

### ملفات التشغيل الرئيسية:
| الملف | الوصف |
|------|-------|
| **`START.bat`** | 🚀 تشغيل المشروع الكامل (Frontend + Backend) |
| **`STOP.bat`** | 🛑 إيقاف جميع السيرفرات |
| **`CHECK_STATUS.bat`** | 🔍 التحقق من حالة المشروع |
| **`TEST.bat`** | 🧪 اختبار الاتصال والسيرفر |

### ملفات أخرى:
| الملف | الوصف |
|------|-------|
| `build_react.bat` | بناء React يدوياً |
| `test_connection.py` | اختبار الاتصال (Python script) |

---

## 🎯 ما الذي يحدث عند تشغيل START.bat؟

### الخطوات التلقائية:

1. **✅ التحقق من المتطلبات**
   - Node.js ✓
   - Python ✓
   - npm ✓

2. **✅ إعداد Python Environment**
   - إنشاء virtual environment (`myenv`)
   - تثبيت المتطلبات الأساسية
   - تثبيت المتطلبات الإضافية (من `requirements_advanced.txt`)

3. **✅ إعداد React Frontend**
   - تثبيت npm packages (`npm install`)
   - بناء المشروع (`npm run build`)
   - إنشاء مجلد `dist` مع الملفات المبنية

4. **✅ التحقق من قاعدة البيانات**
   - إضافة بيانات التدريب الأولية (إذا لم تكن موجودة)

5. **✅ تنظيف السيرفرات القديمة**
   - إيقاف أي سيرفرات قديمة قيد التشغيل

6. **✅ تشغيل FastAPI Backend**
   - تشغيل السيرفر على البورت 8000
   - يخدم React build تلقائياً
   - يعمل في نافذة منفصلة

7. **✅ فتح المتصفح**
   - يفتح http://localhost:8000 تلقائياً

---

## 🌐 الروابط بعد التشغيل

بعد تشغيل `START.bat`، يمكنك الوصول إلى:

| الرابط | الوصف |
|--------|-------|
| **http://localhost:8000** | 🎨 Frontend (Chatbot Interface) |
| **http://localhost:8000/api** | 📝 API Documentation |
| **http://localhost:8000/api/health** | ❤️ Health Check |

---

## 🛑 إيقاف السيرفر

### الطريقة الأولى (الأسهل):
```bash
STOP.bat
```

### الطريقة الثانية (يدوياً):
1. اذهب إلى نافذة "Eva Chatbot - Backend"
2. اضغط `Ctrl+C`
3. أو أغلق النافذة مباشرة

---

## 🔍 التحقق من الحالة

### استخدام CHECK_STATUS.bat:
```bash
CHECK_STATUS.bat
```

هذا الملف يتحقق من:
- ✅ المتطلبات (Node.js, Python)
- ✅ البيئة الافتراضية (`myenv`)
- ✅ React build (`eva-wise-chat-buddy-main/dist`)
- ✅ حالة السيرفر (uvicorn)

### استخدام TEST.bat:
```bash
TEST.bat
```

هذا الملف يقوم بـ:
- ✅ اختبار Health Check API
- ✅ اختبار Chat API
- ✅ اختبار Frontend

---

## 🔧 المتطلبات

قبل التشغيل، تأكد من تثبيت:

| المتطلب | الإصدار المطلوب | رابط التحميل |
|---------|-----------------|---------------|
| **Windows** | 10 أو 11 | - |
| **Node.js** | 16 أو أحدث | https://nodejs.org |
| **Python** | 3.8 أو أحدث | https://python.org |
| **الإنترنت** | - | مطلوب لأول مرة فقط |

---

## ❓ حل المشاكل الشائعة

### المشكلة 1: البورت 8000 مستخدم

**الأعراض:**
```
Error: Address already in use
```

**الحل:**
```bash
STOP.bat
```
أو:
```bash
taskkill /F /IM uvicorn.exe
```

---

### المشكلة 2: React build فشل

**الأعراض:**
```
❌ فشل بناء React!
```

**الحل:**
```bash
cd eva-wise-chat-buddy-main
npm install
npm run build
cd ..
```

أو استخدم:
```bash
build_react.bat
```

---

### المشكلة 3: Python packages مفقودة

**الأعراض:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**الحل:**
```bash
call myenv\Scripts\activate.bat
pip install -r requirements_advanced.txt
```

---

### المشكلة 4: السيرفر لا يبدأ

**الأعراض:**
- لا تظهر نافذة "Eva Chatbot - Backend"
- المتصفح لا يفتح

**الحل:**
1. شغل `CHECK_STATUS.bat` للتحقق من الحالة
2. تأكد من أن Python و Node.js مثبتان:
   ```bash
   python --version
   node --version
   ```
3. تأكد من أن البورت 8000 غير مستخدم:
   ```bash
   netstat -ano | findstr :8000
   ```
4. شغل `START.bat` مرة أخرى

---

### المشكلة 5: Frontend لا يعمل

**الأعراض:**
- صفحة بيضاء أو خطأ 404

**الحل:**
1. تأكد من وجود React build:
   ```bash
   dir eva-wise-chat-buddy-main\dist
   ```
2. إذا لم يكن موجوداً، شغل:
   ```bash
   build_react.bat
   ```
3. أعد تشغيل السيرفر:
   ```bash
   STOP.bat
   START.bat
   ```

---

## 📝 ملاحظات مهمة

### ⚠️ نافذة السيرفر
- السيرفر يعمل في **نافذة منفصلة** اسمها "Eva Chatbot - Backend"
- **لا تغلق هذه النافذة!** إذا أغلقتها، السيرفر سيتوقف
- لإيقاف السيرفر، استخدم `STOP.bat` أو اضغط `Ctrl+C` في النافذة

### ⏱️ وقت التشغيل
- **أول مرة**: قد يستغرق 5-10 دقائق (لتحميل packages)
- **المرات التالية**: 30-60 ثانية فقط

### 🔄 إعادة البناء
- إذا قمت بتعديل React code، شغل `build_react.bat` لإعادة البناء
- إذا قمت بتعديل Python code، السيرفر سيعيد التحميل تلقائياً (reload mode)

---

## 🎨 الميزات

### ✅ ما يعمل تلقائياً:
- ✅ Frontend + Backend متكاملان
- ✅ API متاح على `/api`
- ✅ React build يخدم تلقائياً
- ✅ CORS مفعل
- ✅ Auto-reload للـ Backend
- ✅ Health check endpoint

### 🚀 الميزات المتقدمة:
- ✅ Chat API مع web search
- ✅ Voice processing (speech-to-text, text-to-speech)
- ✅ Image upload
- ✅ Conversation memory
- ✅ Training data collection

---

## 📚 الملفات التوثيقية

| الملف | الوصف |
|------|-------|
| `START_HERE_AR.md` | دليل البدء السريع |
| `README_START.md` | دليل التشغيل |
| `كيفية_التشغيل_السريع.md` | دليل سريع بالعربية |

---

## 🎉 استمتع!

الآن يمكنك استخدام Eva Chatbot! 🚀

**للمساعدة الإضافية:**
- راجع ملف `START_HERE_AR.md`
- شغل `CHECK_STATUS.bat` للتحقق من الحالة
- شغل `TEST.bat` لاختبار الاتصال

---

**تم إنشاء هذا الدليل لمساعدتك في استخدام Eva Chatbot بسهولة! 🎯**

