@echo off
echo ========================================
echo RESTART BACKEND - CLEAN START
echo ========================================
echo.

echo [1/3] Killing old backend processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing PID %%a
    taskkill /PID %%a /F 2>nul
)

timeout /t 3 /nobreak >nul

echo.
echo [2/3] Verifying port is free...
netstat -ano | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port 8001 still in use, waiting...
    timeout /t 5 /nobreak >nul
)

echo.
echo [3/3] Starting fresh backend...
echo.
echo ========================================
echo Backend Starting on http://0.0.0.0:8001
echo Swagger UI: http://127.0.0.1:8001/docs
echo ========================================
echo.
echo Press CTRL+C to stop
echo.

cd /d "%~dp0"
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
