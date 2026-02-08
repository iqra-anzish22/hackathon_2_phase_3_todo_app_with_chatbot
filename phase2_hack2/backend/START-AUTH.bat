@echo off
echo ========================================
echo FastAPI Authentication Backend
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version || (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/3] Checking .env file...
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please copy .env.auth to .env and configure it:
    echo    copy .env.auth .env
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Starting backend...
echo.
echo ========================================
echo Backend: http://127.0.0.1:8001
echo Swagger: http://127.0.0.1:8001/docs
echo Health:  http://127.0.0.1:8001/health
echo ========================================
echo.
echo Press CTRL+C to stop
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
