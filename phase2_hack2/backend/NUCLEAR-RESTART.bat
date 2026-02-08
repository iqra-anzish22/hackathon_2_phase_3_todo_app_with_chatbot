@echo off
echo ========================================
echo NUCLEAR RESTART - Kill Everything
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Killing ALL Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
echo ✅ All Python processes killed

echo.
echo [2/6] Waiting for processes to die...
timeout /t 5 /nobreak >nul

echo.
echo [3/6] Verifying port 8001 is free...
netstat -ano | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Port still in use!
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
        echo Force killing PID %%a
        taskkill /F /PID %%a 2>nul
    )
    timeout /t 3 /nobreak >nul
)
echo ✅ Port is free

echo.
echo [4/6] Deleting ALL cache...
rd /s /q src\__pycache__ 2>nul
rd /s /q src\core\__pycache__ 2>nul
rd /s /q src\api\__pycache__ 2>nul
rd /s /q src\api\routes\__pycache__ 2>nul
rd /s /q src\models\__pycache__ 2>nul
rd /s /q src\schemas\__pycache__ 2>nul
del /s /q *.pyc 2>nul
echo ✅ Cache deleted

echo.
echo [5/6] Verifying new main.py...
findstr /C:"NEW VERSION" src\main.py >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: New main.py not found!
    pause
    exit /b 1
)
echo ✅ New main.py verified

echo.
echo [6/6] Starting FRESH backend (NO RELOAD)...
echo.
echo ========================================
echo 🔐 AUTHENTICATION BACKEND - FINAL START
echo ========================================
echo Swagger: http://127.0.0.1:8001/docs
echo.
echo Expected: "Authentication API - NEW VERSION"
echo.
echo Press CTRL+C to stop
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8001
