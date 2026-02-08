@echo off
echo ========================================
echo Starting FastAPI Backend on port 8001
echo ========================================
echo.
cd /d "%~dp0"
call ..\.venv\Scripts\activate.bat
uvicorn src.main:app --reload --port 8001
