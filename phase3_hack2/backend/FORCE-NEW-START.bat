@echo off
echo ========================================
echo FORCE RESTART - New main.py
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Killing ALL processes on port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F 2>nul
)

echo.
echo [2/4] Deleting ALL Python cache...
rd /s /q src\__pycache__ 2>nul
rd /s /q src\core\__pycache__ 2>nul
rd /s /q src\api\__pycache__ 2>nul
rd /s /q src\api\routes\__pycache__ 2>nul
rd /s /q src\models\__pycache__ 2>nul
rd /s /q src\schemas\__pycache__ 2>nul
del /s /q *.pyc 2>nul
echo ✅ All cache deleted

echo.
echo [3/4] Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Starting with NEW main.py...
echo.
echo ========================================
echo 🔐 AUTHENTICATION BACKEND
echo ========================================
echo Swagger: http://127.0.0.1:8001/docs
echo.
echo Expected: "Authentication API - NEW VERSION"
echo.
echo Press CTRL+C to stop
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
