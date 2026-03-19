# 🎤📷 تكامل الصوت والصور - Voice & Image Integration

## ✅ تم ربط كل شيء بالـ Backend!

### 🎤 الميكروفون (Speech Recognition):

#### الطريقة 1: Browser API (أسرع)
- يستخدم Web Speech API مباشرة
- يعمل في Chrome و Edge
- لا يحتاج Backend

#### الطريقة 2: Backend API (أكثر دقة)
- يسجل الصوت ويُرسله للـ Backend
- معالجة أفضل للعربية
- يعمل حتى لو Browser API غير متاح

**Endpoint:** `/api/voice/speech-to-text`

---

### 🔊 الصوت (Text to Speech):

#### الطريقة 1: Backend API (موصى به)
- جودة أفضل خاصة للعربية
- يستخدم `voice_processing.py`
- يُرجع ملف صوتي

#### الطريقة 2: Browser API (Fallback)
- يعمل في جميع المتصفحات
- أسرع لكن جودة أقل للعربية

**Endpoint:** `/api/voice/text-to-speech`

---

### 📷 الصور (Image Upload):

#### مربوط بالكامل بالـ Backend:
- رفع الصور إلى `/api/upload/image`
- معالجة الصور في `multimedia_processor.py`
- عرض الصور في المحادثة
- دعم جميع الصيغ (JPEG, PNG, GIF, WebP, BMP)

**Endpoint:** `/api/upload/image`

---

## 🔧 كيف يعمل:

### 1. الميكروفون:
```typescript
// يحاول Browser API أولاً
recognitionRef.current.start()

// إذا فشل، يستخدم Audio Recording + Backend
startAudioRecording() → chatService.speechToText()
```

### 2. الصوت:
```typescript
// يحاول Backend أولاً (أفضل جودة)
chatService.textToSpeech() → /api/voice/text-to-speech

// إذا فشل، يستخدم Browser API
window.speechSynthesis.speak()
```

### 3. الصور:
```typescript
// رفع مباشر للـ Backend
chatService.uploadImage() → /api/upload/image
```

---

## 📡 API Endpoints:

### `/api/voice/speech-to-text`
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Body:** 
  - `audio`: ملف صوتي (Blob)
  - `language`: 'ar' أو 'en'
- **Response:** `{ success: true, text: "..." }`

### `/api/voice/text-to-speech`
- **Method:** POST
- **Content-Type:** application/json
- **Body:** 
  ```json
  {
    "text": "النص المراد تحويله",
    "language": "ar"
  }
  ```
- **Response:** ملف صوتي (audio/wav)

### `/api/upload/image`
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Body:** 
  - `file`: ملف صورة
- **Response:** `{ success: true, data: {...} }`

---

## ✅ الميزات:

- ✅ **Hybrid Approach**: Browser API + Backend API
- ✅ **Auto Fallback**: إذا فشل Browser API، يستخدم Backend
- ✅ **دعم العربية**: معالجة أفضل للعربية في Backend
- ✅ **معالجة الأخطاء**: رسائل واضحة للمستخدم
- ✅ **تكامل كامل**: كل شيء مربوط بالـ Backend

---

## 🎯 الاستخدام:

1. **الميكروفون**: اضغط على زر الميكروفون 🎤
2. **الصوت**: اضغط على زر الصوت 🔊
3. **الصور**: اضغط على زر الصورة 📷

---

**تم إنشاء هذا الملف بواسطة Auto - Cursor AI**  
**التاريخ: 2025-01-22**

