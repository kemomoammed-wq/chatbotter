# 🚀 ابدأ من هنا - Eva Chatbot

## ⚡ تشغيل سريع (خطوة واحدة فقط!)

### Windows:
```bash
START.bat
```

**هذا كل شيء!** 🎉

---

## 📁 الملفات المتاحة

### ملفات التشغيل:
- **`START.bat`** - تشغيل المشروع الكامل (Frontend + Backend)
- **`STOP.bat`** - إيقاف السيرفرات
- **`CHECK_STATUS.bat`** - التحقق من حالة المشروع

### ملفات أخرى:
- **`build_react.bat`** - بناء React يدوياً
- **`start_server.bat`** - تشغيل Flask فقط (قديم)
- **`start_server_background.bat`** - تشغيل Flask في الخلفية

---

## 🎯 ما الذي يحدث عند تشغيل START.bat؟

1. ✅ **التحقق من المتطلبات**
   - Node.js
   - Python
   - npm

2. ✅ **إعداد Python Environment**
   - إنشاء virtual environment
   - تثبيت المتطلبات

3. ✅ **إعداد React Frontend**
   - تثبيت npm packages
   - بناء المشروع (إذا لم يكن موجوداً)

4. ✅ **تشغيل Backend**
   - FastAPI على البورت 8000
   - يخدم React build تلقائياً

5. ✅ **فتح المتصفح**
   - يفتح http://localhost:8000 تلقائياً

---

## 🌐 الروابط بعد التشغيل

- **Frontend (Chatbot)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/api/health

---

## 🛑 إيقاف السيرفر

### الطريقة الأولى (الأسهل):
```bash
STOP.bat
```

### الطريقة الثانية (يدوياً):
1. اذهب إلى نافذة "Eva Chatbot - Backend"
2. اضغط `Ctrl+C`
3. أو أغلق النافذة

---

## 🔍 التحقق من الحالة

```bash
CHECK_STATUS.bat
```

هذا الملف يتحقق من:
- ✅ المتطلبات (Node.js, Python)
- ✅ البيئة الافتراضية
- ✅ React build
- ✅ حالة السيرفر

---

## 🔧 المتطلبات

- **Windows**: 10 أو 11
- **Node.js**: الإصدار 16 أو أحدث
- **Python**: 3.8 أو أحدث
- **الإنترنت**: مطلوب لأول مرة فقط

---

## ❓ حل المشاكل الشائعة

### المشكلة: البورت 8000 مستخدم
**الحل:**
```bash
STOP.bat
```
أو:
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
1. شغل `CHECK_STATUS.bat` للتحقق من الحالة
2. تأكد من أن Python و Node.js مثبتان
3. تأكد من أن البورت 8000 غير مستخدم
4. شغل `START.bat` مرة أخرى

---

## 📝 ملاحظات مهمة

- ✅ السيرفر يعمل في **نافذة منفصلة** - لا تغلقها!
- ✅ عند أول تشغيل، قد يستغرق وقتاً أطول (لتحميل packages)
- ✅ بعد البناء الأول، التشغيل التالي سيكون أسرع
- ✅ يمكنك إعادة بناء React يدوياً باستخدام `build_react.bat`

---

## 🎉 استمتع!

الآن يمكنك استخدام Eva Chatbot! 🚀

**للمساعدة الإضافية**: راجع ملف `README_START.md`

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. شغل `CHECK_STATUS.bat` للتحقق من الحالة
2. راجع ملف `كيفية_التشغيل_السريع.md`
3. تأكد من أن جميع المتطلبات مثبتة

---

**تم إنشاء هذا الملف لمساعدتك في البدء بسرعة! 🎯**
