@echo off
echo ========================================
echo AUTHENTICATION SYSTEM VERIFICATION
echo ========================================
echo.

cd /d "%~dp0"

echo [Step 1] Checking if backend is running...
curl -s http://127.0.0.1:8001/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend is NOT running
    echo.
    echo Please start backend first:
    echo    CLEAN-START.bat
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Backend is running
)

echo.
echo [Step 2] Checking authentication endpoints...
curl -s http://127.0.0.1:8001/openapi.json > openapi_temp.json 2>&1

findstr /C:"api/auth/signup" openapi_temp.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Signup endpoint NOT found
) else (
    echo ✅ Signup endpoint found: POST /api/auth/signup
)

findstr /C:"api/auth/signin" openapi_temp.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Signin endpoint NOT found
) else (
    echo ✅ Signin endpoint found: POST /api/auth/signin
)

findstr /C:"api/auth/me" openapi_temp.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Me endpoint NOT found
) else (
    echo ✅ Me endpoint found: GET /api/auth/me
)

del openapi_temp.json 2>nul

echo.
echo [Step 3] Testing signup endpoint...
set TEST_EMAIL=verify_%RANDOM%@example.com

curl -s -X POST http://127.0.0.1:8001/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"testpass123\",\"name\":\"Verify User\"}" ^
  > signup_test.json 2>&1

findstr /C:"access_token" signup_test.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Signup FAILED
    echo Response:
    type signup_test.json
) else (
    echo ✅ Signup SUCCESSFUL
    echo Email: %TEST_EMAIL%
)

echo.
echo [Step 4] Testing signin endpoint...
curl -s -X POST http://127.0.0.1:8001/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"testpass123\"}" ^
  > signin_test.json 2>&1

findstr /C:"access_token" signin_test.json >nul 2>&1
if errorlevel 1 (
    echo ❌ Signin FAILED
    echo Response:
    type signin_test.json
) else (
    echo ✅ Signin SUCCESSFUL
)

echo.
echo ========================================
echo VERIFICATION COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Open Swagger UI: http://127.0.0.1:8001/docs
echo 2. Look for "Authentication" section
echo 3. Test signup/signin in the browser
echo.
echo If endpoints don't appear in Swagger:
echo - Open in INCOGNITO/PRIVATE window
echo - Press Ctrl+Shift+R to hard refresh
echo - Clear browser cache completely
echo.

del signup_test.json signin_test.json 2>nul

pause
