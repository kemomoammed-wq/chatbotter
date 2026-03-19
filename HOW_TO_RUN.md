# 🚀 كيفية تشغيل التطبيق

## الطريقة السهلة (موصى بها)

### 1. تشغيل كل شيء معاً (FastAPI + React Build)
```bash
START_ALL.bat
```

**ماذا يفعل:**
- ✅ يشغل FastAPI على `http://localhost:8000`
- ✅ يخدم React build (إذا كان موجوداً)
- ✅ يوفر جميع API endpoints
- ✅ يعمل تلقائياً مع جميع التحسينات

**المميزات:**
- سهل الاستخدام - ملف واحد فقط
- يعمل مع React build الموجود
- مناسب للإنتاج

---

## الطريقة المتقدمة (للتطوير)

### 2. تشغيل في وضع التطوير (React Dev + FastAPI)
```bash
START_DEV.bat
```

**ماذا يفعل:**
- ✅ يشغل FastAPI على `http://localhost:8000`
- ✅ يشغل React Dev Server على `http://localhost:5173`
- ✅ Hot reload للـ React
- ✅ Hot reload للـ FastAPI

**المميزات:**
- مناسب للتطوير
- تحديثات فورية
- نافذتان منفصلتان

---

## الطرق اليدوية

### 3. تشغيل FastAPI فقط
```bash
start_server.bat
```
أو:
```bash
myenv\Scripts\activate
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. بناء React ثم تشغيل
```bash
# بناء React
cd eva-wise-chat-buddy-main
npm install
npm run build
cd ..

# تشغيل FastAPI
start_server.bat
```

---

## 📍 الروابط بعد التشغيل

### FastAPI Server
- **الرئيسي:** http://localhost:8000
- **API:** http://localhost:8000/api
- **Health Check:** http://localhost:8000/api/health

### React Frontend
- **في وضع الإنتاج:** http://localhost:8000 (يُخدم من FastAPI)
- **في وضع التطوير:** http://localhost:5173 (React Dev Server)

### API Endpoints المهمة
- **Chat:** http://localhost:8000/api/chat
- **Training Quality:** http://localhost:8000/api/training/quality
- **Training Stats:** http://localhost:8000/api/training/statistics
- **Export Training:** http://localhost:8000/api/training/export

---

## 🔧 المتطلبات

### Python
- Python 3.8+
- Virtual environment (myenv)
- المتطلبات من `requirements.txt`

### Node.js (للتطوير فقط)
- Node.js 16+
- npm أو yarn

---

## ⚠️ ملاحظات مهمة

1. **أول مرة:**
   - سيتم إنشاء البيئة الافتراضية تلقائياً
   - سيتم تثبيت المتطلبات تلقائياً

2. **React Build:**
   - إذا لم يكن موجوداً، سيتم السؤال عن بناءه
   - أو استخدم `build_react.bat`

3. **البورتات:**
   - FastAPI: 8000
   - React Dev: 5173
   - تأكد من عدم استخدامها من برامج أخرى

4. **الإيقاف:**
   - اضغط `Ctrl+C` في نافذة السيرفر
   - أو استخدم `STOP.bat`

---

## 🐛 حل المشاكل

### المشكلة: البورت 8000 مستخدم
```bash
# إيقاف العمليات القديمة
taskkill /F /IM uvicorn.exe
taskkill /F /IM python.exe
```

### المشكلة: React build غير موجود
```bash
cd eva-wise-chat-buddy-main
npm install
npm run build
cd ..
```

### المشكلة: متطلبات Python غير مثبتة
```bash
myenv\Scripts\activate
pip install -r requirements.txt
```

---

## ✅ التحقق من العمل

1. افتح: http://localhost:8000/api/health
2. يجب أن ترى: `{"status":"ok"}`

3. افتح: http://localhost:8000/api/training/quality
4. يجب أن ترى إحصائيات التدريب

---

## 🎉 جاهز!

بعد التشغيل، يمكنك:
- ✅ استخدام التطبيق من المتصفح
- ✅ استدعاء API endpoints
- ✅ مراقبة السجلات في `logs/chatbot.log`
- ✅ تصدير بيانات التدريب

**استمتع!** 🚀

