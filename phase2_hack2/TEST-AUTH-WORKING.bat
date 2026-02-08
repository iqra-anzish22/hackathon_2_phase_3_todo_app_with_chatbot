@echo off
echo ========================================
echo Testing Authentication Flow
echo ========================================
echo.

echo [1/3] Testing Backend Health...
curl -s http://127.0.0.1:8001/health
echo.
echo.

echo [2/3] Testing Signup (new user)...
curl -s -X POST http://127.0.0.1:8001/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -H "Origin: http://localhost:3000" ^
  -d "{\"email\":\"demo@example.com\",\"password\":\"demo12345\"}"
echo.
echo.

echo [3/3] Testing Signin (existing user)...
curl -s -X POST http://127.0.0.1:8001/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -H "Origin: http://localhost:3000" ^
  -d "{\"email\":\"newuser@test.com\",\"password\":\"testpass123\"}"
echo.
echo.

echo ========================================
echo All tests completed!
echo ========================================
echo.
echo Backend is running on: http://127.0.0.1:8001
echo Frontend should be on: http://localhost:3000
echo.
echo Try signing up at: http://localhost:3000/signup
echo Try signing in at: http://localhost:3000/signin
echo.
pause
