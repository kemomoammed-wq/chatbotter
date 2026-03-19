# 🤖 Eva Smart Chatbot - شات بوت ذكي متكامل

## 🎯 نظرة عامة

شات بوت ذكي متكامل مبني بـ **FastAPI** للـ Backend و **React** للـ Frontend. يدعم المحادثات الفورية، البحث في الإنترنت التلقائي، الميكروفون، حفظ البيانات، ونظام تدريب متقدم.

---

## ⚡ التشغيل السريع

### خطوة واحدة فقط! 🚀

**انقر نقراً مزدوجاً على:** `start_server.bat`

ثم افتح المتصفح: **http://localhost:8000**

**✅ انتهيت! التطبيق يعمل الآن**

---

## 📋 المتطلبات

### Backend
- Python 3.8+
- جميع المكتبات في `requirements_advanced.txt`

### Frontend
- Node.js 18+ (للبناء فقط)
- React Build موجود في `eva-wise-chat-buddy-main/dist`

---

## 🚀 التشغيل

### الطريقة 1: ملف Batch (الأسهل) ⭐

```batch
start_server.bat
```

### الطريقة 2: PowerShell

```powershell
cd C:\Users\WIN11-2025-\Desktop\chatot
.\myenv\Scripts\activate
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

### الطريقة 3: في الخلفية

```batch
start_server_background.bat
```

---

## 📡 API Endpoints

| Endpoint | Method | الوصف |
|----------|--------|-------|
| `/api/health` | GET | فحص صحة السيرفر |
| `/api/chat` | POST | إرسال رسالة |
| `/api/conversations` | GET | استرجاع المحادثات |
| `/api/training` | GET | استرجاع عينات التدريب |
| `/api/links` | GET, POST | إدارة الروابط |
| `/api/search` | POST | بحث في الويب |
| `/api/voice/speech-to-text` | POST | الميكروفون |
| `/api/voice/text-to-speech` | POST | تحويل النص إلى كلام |
| `/api/upload/image` | POST | رفع صور |

---

## 🎨 المميزات

### ✅ الوظائف الأساسية
- شات بوت ذكي يرد على الرسائل
- بحث تلقائي في الإنترنت
- حفظ جميع المحادثات
- نظام تدريب متقدم

### ✅ المميزات المتقدمة
- الميكروفون (Speech-to-Text)
- تحويل النص إلى كلام
- رفع ومعالجة الصور
- إدارة الروابط
- شكل رسائل محسّن

---

## 🗄️ قاعدة البيانات

- **الموقع:** `logs/chatbot.db`
- **النوع:** SQLite
- **الجداول:**
  - `conversations` - المحادثات
  - `training_samples` - عينات التدريب
  - `scraped_data` - البيانات المستخرجة
  - `medical_data` - البيانات الطبية

---

## 📁 الملفات المهمة

| الملف | الوصف |
|------|-------|
| `fastapi_app.py` | FastAPI Server الرئيسي |
| `database.py` | إدارة قاعدة البيانات |
| `start_server.bat` | تشغيل السيرفر |
| `stop_server.bat` | إيقاف السيرفر |
| `check_server.bat` | فحص حالة السيرفر |
| `PROJECT_DELIVERY.md` | دليل التسليم الشامل |
| `كيفية_التشغيل.md` | دليل التشغيل بالعربية |

---

## 🧪 الاختبار

### اختبار سريع

```powershell
# فحص الصحة
Invoke-RestMethod -Uri http://localhost:8000/api/health

# إرسال رسالة
$body = @{message="مرحباً"; user_id="test"} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/api/chat -Method Post -ContentType 'application/json' -Body $body
```

---

## 🐛 حل المشاكل

### السيرفر لا يعمل
```batch
stop_server.bat
start_server.bat
```

### البورت 8000 مشغول
```powershell
Get-Process uvicorn | Stop-Process -Force
```

### الواجهة لا تظهر
```powershell
cd eva-wise-chat-buddy-main
npm run build
cd ..
```

---

## 📊 حالة المشروع

**✅ الحالة:** جاهز للتسليم  
**📅 التاريخ:** 2025-12-11  
**🔢 الإصدار:** 1.0.0

---

## 📞 الدعم

للمزيد من التفاصيل، راجع:
- `PROJECT_DELIVERY.md` - دليل التسليم الشامل
- `كيفية_التشغيل.md` - دليل التشغيل
- `START_HERE_AR.md` - دليل سريع

---

**🎉 المشروع جاهز للاستخدام!**

