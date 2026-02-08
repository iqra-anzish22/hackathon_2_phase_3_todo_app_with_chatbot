@echo off
REM ========================================
REM Clean Start Script for FastAPI Backend
REM ========================================

echo.
echo ========================================
echo Cleaning up old processes...
echo ========================================

REM Kill any existing processes on port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing process %%a
    taskkill /PID %%a /F 2>nul
)

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting Fresh FastAPI Backend
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version || (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo [2/4] Checking .env file...
if not exist .env (
    echo ERROR: .env file not found!
    echo Please ensure .env exists in backend folder
    pause
    exit /b 1
)

echo [3/4] Installing dependencies...
pip install -q -r requirements.txt

echo [4/4] Starting backend server...
echo.
echo ========================================
echo Backend Starting on http://127.0.0.1:8001
echo Swagger UI: http://127.0.0.1:8001/docs
echo ========================================
echo.
echo IMPORTANT: Open Swagger UI in INCOGNITO/PRIVATE window
echo to avoid cache issues!
echo.
echo Press CTRL+C to stop
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
