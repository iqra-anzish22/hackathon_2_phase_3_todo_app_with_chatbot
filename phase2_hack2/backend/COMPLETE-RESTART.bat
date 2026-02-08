@echo off
echo ========================================
echo COMPLETE RESTART - Authentication Backend
echo ========================================
echo.

echo [1/4] Killing ALL old backend processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing PID %%a
    taskkill /PID %%a /F 2>nul
)

echo Waiting for port to clear...
timeout /t 5 /nobreak >nul

echo.
echo [2/4] Verifying .env file...
if not exist .env (
    echo Copying .env.auth to .env...
    copy /Y .env.auth .env >nul
)

echo.
echo [3/4] Verifying port is free...
netstat -ano | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Port 8001 still in use!
    echo Waiting 5 more seconds...
    timeout /t 5 /nobreak >nul
)

echo.
echo [4/4] Starting FRESH backend with AUTH routes...
echo.
echo ========================================
echo Backend: http://127.0.0.1:8001
echo Swagger: http://127.0.0.1:8001/docs
echo ========================================
echo.
echo You should see:
echo   - POST /api/auth/signup
echo   - POST /api/auth/signin
echo   - GET  /api/auth/me
echo.
echo Press CTRL+C to stop
echo.

cd /d "%~dp0"
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
