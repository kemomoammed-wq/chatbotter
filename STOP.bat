@echo off
chcp 65001 >nul
REM ============================================
REM 🛑 إيقاف Eva Chatbot
REM ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              🛑 إيقاف Eva Chatbot                          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/2] 🛑 إيقاف السيرفرات...

REM إيقاف uvicorn
taskkill /F /IM uvicorn.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ تم إيقاف uvicorn (FastAPI)
) else (
    echo ℹ️  لا توجد عملية uvicorn قيد التشغيل
)

REM إيقاف React Dev Server (Vite)
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ تم إيقاف React Dev Server
) else (
    echo ℹ️  لا توجد عملية React Dev Server قيد التشغيل
)

REM إيقاف Python processes المتعلقة بالمشروع (بحذر)
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /C:"PID:"') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 1 /nobreak >nul

echo.
echo [2/2] 🧹 تنظيف الملفات المؤقتة...

del start_backend.bat 2>nul

echo.
echo ✅ تم إيقاف جميع السيرفرات بنجاح!
echo.
pause

