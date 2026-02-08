@echo off
echo ========================================
echo Starting FastAPI Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Checking if .env file exists...
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env file from .env.example
    pause
    exit /b 1
)

echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo Starting Backend on http://127.0.0.1:8001
echo Swagger UI: http://127.0.0.1:8001/docs
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
