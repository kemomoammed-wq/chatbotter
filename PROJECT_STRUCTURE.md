# 📁 هيكل المشروع - Project Structure

## 📂 الملفات الرئيسية

### 🚀 التشغيل
- **`START_HERE.md`** - ⭐ ابدأ من هنا! دليل التشغيل خطوة بخطوة
- **`README.md`** - الدليل الشامل للمشروع
- **`run_integrated.bat`** - تشغيل موحد (Windows)
- **`run_integrated.sh`** - تشغيل موحد (Linux/Mac)
- **`build_react.bat`** - بناء React

### 🐍 Python Backend

#### السيرفر الرئيسي
- **`app.py`** - Flask server (يخدم React + API)

#### التكامل والبنية التحتية
- **`core_integration.py`** - نظام التكامل المركزي
- **`database.py`** - إدارة قاعدة البيانات
- **`setup_advanced_chatbot.py`** - إعداد أولي

#### الميزات المتقدمة
- **`multimedia_processor.py`** - معالجة الوسائط المتعددة
- **`streaming_handler.py`** - معالجة Streaming
- **`memory_manager.py`** - إدارة الذاكرة والمحادثات
- **`tools_layer.py`** - طبقة الأدوات

#### الذكاء الاصطناعي
- **`advanced_chatbot_integration.py`** - الشاتبوت المتقدم
- **`llm_integration.py`** - تكامل LLM
- **`web_search_service.py`** - البحث على الويب
- **`web_scraper.py`** - استخراج البيانات
- **`scraper_manager.py`** - إدارة الاستخراج
- **`ai_knowledge_base.py`** - قاعدة المعرفة
- **`conversation_memory.py`** - ذاكرة المحادثات
- **`vector_database.py`** - قاعدة البيانات المتجهة

#### معالجة البيانات
- **`nlp_preprocessing.py`** - معالجة النصوص
- **`data_preprocessing.py`** - معالجة البيانات
- **`advanced_features.py`** - ميزات متقدمة
- **`ai_enhancements.py`** - تحسينات AI

#### النماذج والتدريب
- **`model_training.py`** - تدريب النماذج
- **`advanced_training.py`** - تدريب متقدم
- **`bilstm_model.py`** - نموذج BiLSTM

#### أدوات مساعدة
- **`analytics_dashboard.py`** - لوحة التحليلات
- **`advanced_caching.py`** - التخزين المؤقت
- **`voice_processing.py`** - معالجة الصوت
- **`web_scraper_utils.py`** - أدوات مساعدة

### ⚛️ React Frontend
- **`eva-wise-chat-buddy-main/`** - مجلد React
  - **`src/`** - الكود المصدري
  - **`dist/`** - Build files (يُخدم من Flask)
  - **`package.json`** - المتطلبات
  - **`vite.config.ts`** - إعداد Vite

### 📚 التوثيق
- **`AI_MASTER_ROADMAP.md`** - دليل شامل في الذكاء الاصطناعي

### 📦 الإعداد
- **`requirements_advanced.txt`** - متطلبات Python

---

## 🔄 تدفق العمل

```
المستخدم
   ↓
React Frontend (http://localhost:5000)
   ↓
Flask API (/api/*)
   ↓
Core Integration
   ↓
Chatbot + AI Modules
   ↓
Database / Web Search / Tools
   ↓
Response
```

---

## 📝 ملاحظات

- جميع الملفات متصلة من خلال `core_integration.py`
- Flask يخدم React build files من `eva-wise-chat-buddy-main/dist`
- API endpoints تحت `/api/*`
- المحادثات تُحفظ في `logs/chatbot.db`

---

**تم إنشاء هذا الملف بواسطة Auto - Cursor AI**

