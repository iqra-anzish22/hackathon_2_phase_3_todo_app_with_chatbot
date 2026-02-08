@echo off
echo ========================================
echo COMPLETE AUTHENTICATION TEST
echo ========================================
echo.

echo [1/5] Checking Backend Status...
curl -s http://127.0.0.1:8001/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend is NOT running on port 8001
    echo.
    echo Please start backend:
    echo    cd backend
    echo    uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Backend is running
)

echo.
echo [2/5] Testing Signup Endpoint...
set TEST_EMAIL=test_%RANDOM%@example.com
curl -s -X POST http://127.0.0.1:8001/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"testpass123\",\"name\":\"Test User\"}" ^
  > test_signup.json 2>&1

findstr /C:"access_token" test_signup.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Signup FAILED
    echo Response:
    type test_signup.json
    del test_signup.json 2>nul
    pause
    exit /b 1
) else (
    echo ✅ Signup endpoint working
    echo    Email: %TEST_EMAIL%
)

echo.
echo [3/5] Testing Signin Endpoint...
curl -s -X POST http://127.0.0.1:8001/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"testpass123\"}" ^
  > test_signin.json 2>&1

findstr /C:"access_token" test_signin.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Signin FAILED
    echo Response:
    type test_signin.json
    del test_signup.json test_signin.json 2>nul
    pause
    exit /b 1
) else (
    echo ✅ Signin endpoint working
)

echo.
echo [4/5] Testing Protected Endpoint...
for /f "tokens=2 delims=:," %%a in ('type test_signin.json ^| findstr "access_token"') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN: =%

curl -s -X GET http://127.0.0.1:8001/api/auth/me ^
  -H "Authorization: Bearer %TOKEN%" ^
  > test_me.json 2>&1

findstr /C:"email" test_me.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Protected endpoint FAILED
    echo Response:
    type test_me.json
    del test_signup.json test_signin.json test_me.json 2>nul
    pause
    exit /b 1
) else (
    echo ✅ Protected endpoint working
)

echo.
echo [5/5] Checking Frontend Configuration...
if not exist ..\frontend\.env.local (
    echo ❌ Frontend .env.local NOT found
    del test_signup.json test_signin.json test_me.json 2>nul
    pause
    exit /b 1
)

findstr /C:"NEXT_PUBLIC_API_URL=http://127.0.0.1:8001" ..\frontend\.env.local >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Frontend API URL might be incorrect
    echo    Check frontend/.env.local has: NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
) else (
    echo ✅ Frontend configuration correct
)

del test_signup.json test_signin.json test_me.json 2>nul

echo.
echo ========================================
echo ✅ ALL TESTS PASSED!
echo ========================================
echo.
echo Your authentication system is working perfectly!
echo.
echo Next steps:
echo 1. Ensure frontend is running: npm run dev
echo 2. Open: http://localhost:3000/signup
echo 3. Create an account
echo 4. You should be automatically signed in!
echo.
echo Backend: http://127.0.0.1:8001/docs
echo Frontend: http://localhost:3000
echo.
pause
