@echo off
REM Batch script لتشغيل migrations على Windows
echo ========================================
echo Database Migration Tool
echo ========================================
echo.

if "%1"=="" (
    echo Applying all migrations...
    alembic upgrade head
) else if "%1"=="--init" (
    echo Creating initial migration...
    alembic revision --autogenerate -m "Initial migration"
    echo.
    echo Migration created! Run without arguments to apply it.
) else if "%1"=="--upgrade" (
    echo Upgrading database...
    alembic upgrade head
) else if "%1"=="--downgrade" (
    echo Downgrading database...
    alembic downgrade -1
) else if "%1"=="--current" (
    echo Current migration version:
    alembic current
) else if "%1"=="--history" (
    echo Migration history:
    alembic history
) else (
    echo Unknown option: %1
    echo Usage:
    echo   run_migrations.bat          - Apply all migrations
    echo   run_migrations.bat --init   - Create initial migration
    echo   run_migrations.bat --upgrade - Upgrade database
    echo   run_migrations.bat --downgrade - Downgrade database
    echo   run_migrations.bat --current - Show current version
    echo   run_migrations.bat --history - Show migration history
)

pause

