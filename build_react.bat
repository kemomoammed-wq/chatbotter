@echo off
REM ============================================
REM بناء React للتكامل مع Flask
REM ============================================

echo.
echo ============================================
echo 🔨 بناء React
echo ============================================
echo.

cd eva-wise-chat-buddy-main

if not exist "node_modules" (
    echo 📦 تثبيت المتطلبات...
    call npm install
)

echo.
echo 🔨 بناء React...
call npm run build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ تم بناء React بنجاح!
    echo 📁 الملفات في: eva-wise-chat-buddy-main\dist
) else (
    echo.
    echo ❌ فشل بناء React!
)

cd ..
pause

