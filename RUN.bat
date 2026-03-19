@echo off
chcp 65001 >nul
REM ============================================
REM 🚀 تشغيل التطبيق الكامل مع معالجة الأخطاء
REM ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║          🚀 تشغيل Eva Chatbot - التطبيق الكامل          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM التحقق من وجود Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python غير مثبت!
    echo 💡 يرجى تثبيت Python من https://python.org
    pause
    exit /b 1
)

REM التحقق من وجود البيئة الافتراضية
if not exist "myenv\Scripts\activate.bat" (
    echo.
    echo 📦 إنشاء البيئة الافتراضية...
    python -m venv myenv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ فشل إنشاء البيئة الافتراضية!
        pause
        exit /b 1
    )
    echo ✅ تم إنشاء البيئة الافتراضية بنجاح
)

REM تفعيل البيئة الافتراضية
echo.
echo 🔧 تفعيل البيئة الافتراضية...
call myenv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ خطأ: فشل تفعيل البيئة الافتراضية
    pause
    exit /b 1
)
echo ✅ تم تفعيل البيئة الافتراضية

REM التحقق من تثبيت المتطلبات الأساسية
echo.
echo 📦 التحقق من المتطلبات...
python -c "import fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 تثبيت المتطلبات الأساسية...
    pip install fastapi uvicorn[standard] >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ⚠️  تحذير: قد تحتاج لتثبيت المتطلبات يدوياً
        echo 💡 جرب: pip install -r requirements.txt
    ) else (
        echo ✅ تم تثبيت المتطلبات الأساسية
    )
)

REM التحقق من باقي المتطلبات
python -c "import sqlalchemy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 تثبيت sqlalchemy...
    pip install sqlalchemy >nul 2>&1
)

REM تثبيت المتطلبات الإضافية
python -c "import beautifulsoup4" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 تثبيت beautifulsoup4...
    pip install beautifulsoup4 >nul 2>&1
)

python -c "import requests" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 تثبيت requests...
    pip install requests >nul 2>&1
)

REM تثبيت ddgs للبحث
python -c "import ddgs" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 تثبيت ddgs (للبحث في الإنترنت)...
    pip install ddgs >nul 2>&1
)

REM تثبيت nltk (اختياري - للنصوص المتقدمة)
python -c "import nltk" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 📦 تثبيت nltk (اختياري)...
    pip install nltk >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 📥 تحميل بيانات nltk...
        python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)" >nul 2>&1
    )
)

REM إنشاء مجلدات ضرورية
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data

REM إيقاف أي سيرفرات قديمة
echo.
echo 🛑 إيقاف السيرفرات القديمة...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul

REM التحقق من البورت
netstat -ano | findstr ":8000" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ⚠️  البورت 8000 مستخدم!
    echo 💡 جاري محاولة إيقاف العمليات...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a 2>nul
    )
    timeout /t 2 /nobreak >nul
)

REM عرض معلومات التشغيل
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                    ✅ كل شيء جاهز!                      ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🌐 FastAPI Server: http://localhost:8000
echo 📝 API Endpoints: http://localhost:8000/api
echo ❤️  Health Check: http://localhost:8000/api/health
echo 📊 Training: http://localhost:8000/api/training/quality
echo.
if exist "eva-wise-chat-buddy-main\dist" (
    echo 🎨 React Frontend: http://localhost:8000
    echo    (يتم خدمته من FastAPI)
) else (
    echo ⚠️  React build غير موجود
    echo 💡 لبناء React: cd eva-wise-chat-buddy-main ^&^& npm run build
)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ⚡ اضغط Ctrl+C لإيقاف السيرفر
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM تشغيل FastAPI مع معالجة الأخطاء
python -c "import fastapi_app" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ خطأ في تحميل fastapi_app!
    echo 💡 تحقق من وجود جميع الملفات المطلوبة
    pause
    exit /b 1
)

echo 🚀 بدء تشغيل السيرفر...
echo.

uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ فشل تشغيل السيرفر!
    echo 💡 تحقق من:
    echo    - وجود جميع المتطلبات
    echo    - عدم استخدام البورت 8000
    echo    - صحة ملفات المشروع
    pause
    exit /b 1
)

pause

