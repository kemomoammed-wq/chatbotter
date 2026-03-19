#!/bin/bash
# ============================================
# تشغيل المشروع المتكامل (React + Python)
# ============================================

echo ""
echo "============================================"
echo "🚀 تشغيل المشروع المتكامل"
echo "============================================"
echo ""

# التحقق من وجود Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js غير مثبت!"
    echo "💡 يرجى تثبيت Node.js من https://nodejs.org"
    exit 1
fi

# التحقق من وجود Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python غير مثبت!"
    echo "💡 يرجى تثبيت Python من https://python.org"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)

# الانتقال إلى مجلد React
cd eva-wise-chat-buddy-main || exit 1

# التحقق من وجود node_modules
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 تثبيت متطلبات React..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ فشل تثبيت متطلبات React!"
        exit 1
    fi
fi

# التحقق من وجود build
if [ ! -d "dist" ]; then
    echo ""
    echo "🔨 بناء React..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ فشل بناء React!"
        exit 1
    fi
    echo "✅ تم بناء React بنجاح!"
else
    echo "✅ React build موجود"
fi

# العودة للمجلد الرئيسي
cd ..

# التحقق من وجود البيئة الافتراضية
if [ ! -d "myenv" ]; then
    echo ""
    echo "📦 إنشاء البيئة الافتراضية..."
    $PYTHON_CMD -m venv myenv
    if [ $? -ne 0 ]; then
        echo "❌ فشل إنشاء البيئة الافتراضية!"
        exit 1
    fi
fi

# تفعيل البيئة الافتراضية
echo ""
echo "🔧 تفعيل البيئة الافتراضية..."
source myenv/bin/activate

# التحقق من تثبيت المتطلبات
echo ""
echo "📦 التحقق من متطلبات Python..."
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 تثبيت متطلبات Python..."
    pip install flask flask-cors pillow
    if [ $? -ne 0 ]; then
        echo "❌ فشل تثبيت المتطلبات!"
        exit 1
    fi
fi

# تشغيل Flask
echo ""
echo "============================================"
echo "✅ كل شيء جاهز!"
echo "============================================"
echo ""
echo "🌐 السيرفر سيعمل على: http://localhost:5000"
echo "📝 API: http://localhost:5000/api"
echo "❤️  Health Check: http://localhost:5000/api/health"
echo ""
echo "============================================"
echo ""

python app.py

