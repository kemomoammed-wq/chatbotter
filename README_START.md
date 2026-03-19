# 🚀 Eva Chatbot - دليل التشغيل السريع

## ⚡ تشغيل سريع (خطوة واحدة)

### Windows:
```bash
START.bat
```

**هذا كل شيء!** الملف سيقوم بكل شيء تلقائياً:
- ✅ التحقق من المتطلبات
- ✅ إعداد البيئة
- ✅ بناء React
- ✅ تشغيل Backend
- ✅ فتح المتصفح

---

## 📋 ما الذي يحدث عند التشغيل؟

1. **التحقق من المتطلبات**
   - Node.js ✓
   - Python ✓
   - npm ✓

2. **إعداد Python Environment**
   - إنشاء virtual environment
   - تثبيت المتطلبات

3. **إعداد React Frontend**
   - تثبيت npm packages
   - بناء المشروع

4. **تشغيل Backend**
   - FastAPI على البورت 8000
   - يخدم React build تلقائياً

5. **فتح المتصفح**
   - يفتح http://localhost:8000 تلقائياً

---

## 🌐 الروابط

بعد التشغيل، يمكنك الوصول إلى:

- **Frontend (Chatbot)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/api/health

---

## 🛑 إيقاف السيرفر

1. اذهب إلى نافذة "Eva Chatbot - Backend"
2. اضغط `Ctrl+C`
3. أو أغلق النافذة

---

## 🔧 المتطلبات

- **Windows**: 10 أو 11
- **Node.js**: الإصدار 16 أو أحدث
- **Python**: 3.8 أو أحدث
- **الإنترنت**: مطلوب لأول مرة فقط (لتحميل packages)

---

## ❓ حل المشاكل

### المشكلة: البورت 8000 مستخدم
**الحل:**
```bash
taskkill /F /IM uvicorn.exe
```

### المشكلة: React build فشل
**الحل:**
```bash
cd eva-wise-chat-buddy-main
npm install
npm run build
cd ..
```

### المشكلة: Python packages مفقودة
**الحل:**
```bash
call myenv\Scripts\activate.bat
pip install -r requirements_advanced.txt
```

### المشكلة: السيرفر لا يبدأ
**الحل:**
1. تأكد من أن Python و Node.js مثبتان
2. تأكد من أن البورت 8000 غير مستخدم
3. شغل `START.bat` مرة أخرى

---

## 📝 ملاحظات مهمة

- ✅ السيرفر يعمل في **نافذة منفصلة** - لا تغلقها!
- ✅ عند أول تشغيل، قد يستغرق وقتاً أطول (لتحميل packages)
- ✅ بعد البناء الأول، التشغيل التالي سيكون أسرع
- ✅ يمكنك إعادة بناء React يدوياً باستخدام `build_react.bat`

---

## 🎉 استمتع!

الآن يمكنك استخدام Eva Chatbot! 🚀

---

**للمساعدة**: راجع ملف `كيفية_التشغيل_السريع.md`

