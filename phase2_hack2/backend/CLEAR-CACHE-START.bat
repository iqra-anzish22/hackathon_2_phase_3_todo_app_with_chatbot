@echo off
echo ========================================
echo COMPLETE FIX - Clear Cache and Restart
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Stopping ALL backend processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing PID %%a
    taskkill /PID %%a /F 2>nul
)
timeout /t 3 /nobreak >nul

echo.
echo [2/5] Clearing Python cache...
echo Deleting __pycache__ folders...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo Deleting .pyc files...
del /s /q *.pyc 2>nul
echo ✅ Cache cleared

echo.
echo [3/5] Verifying .env file...
if not exist .env (
    echo Creating .env from template...
    copy /Y .env.auth .env >nul
)

echo.
echo [4/5] Waiting for port to clear...
timeout /t 3 /nobreak >nul

echo.
echo [5/5] Starting FRESH backend (no cache)...
echo.
echo ========================================
echo Backend: http://127.0.0.1:8001
echo Swagger: http://127.0.0.1:8001/docs
echo ========================================
echo.
echo Expected endpoints:
echo   ✅ POST /api/auth/signup
echo   ✅ POST /api/auth/signin
echo   ✅ GET  /api/auth/me
echo.
echo Press CTRL+C to stop
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
