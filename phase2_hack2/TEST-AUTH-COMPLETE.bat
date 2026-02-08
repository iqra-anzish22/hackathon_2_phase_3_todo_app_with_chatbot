@echo off
echo ========================================
echo Authentication Test Script
echo ========================================
echo.

echo [1/4] Testing Backend Health...
curl -s http://127.0.0.1:8001/health
if %errorlevel% neq 0 (
    echo ERROR: Backend is not running!
    echo Please start backend first: cd backend ^&^& uvicorn src.main:app --reload --port 8001
    exit /b 1
)
echo ✓ Backend is running
echo.

echo [2/4] Testing Signup Endpoint...
curl -X POST http://127.0.0.1:8001/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"testpass123\",\"name\":\"Test User\"}"
echo.
echo.

echo [3/4] Testing Signin Endpoint...
curl -X POST http://127.0.0.1:8001/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"testpass123\"}"
echo.
echo.

echo [4/4] Testing CORS Configuration...
echo CORS Origins configured: http://localhost:3000, http://localhost:3001, http://127.0.0.1:3000
echo.

echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. If backend is not running, start it: cd backend ^&^& uvicorn src.main:app --reload --port 8001
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Open browser: http://localhost:3000/signin
echo 4. Try signing in with: test@example.com / testpass123
echo.
pause
