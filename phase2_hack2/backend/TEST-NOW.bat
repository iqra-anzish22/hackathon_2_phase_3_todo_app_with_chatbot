@echo off
echo ========================================
echo Testing NEW Backend
echo ========================================
echo.

echo [1/3] Testing Root Endpoint...
curl -s http://127.0.0.1:8001/
echo.
echo.

echo [2/3] Testing Signup...
curl -s -X POST http://127.0.0.1:8001/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"finaltest@example.com\",\"password\":\"testpass123\",\"name\":\"Final Test\"}"
echo.
echo.

echo [3/3] Opening Swagger UI...
start http://127.0.0.1:8001/docs
echo.
echo Check browser for Swagger UI!
echo.
pause
