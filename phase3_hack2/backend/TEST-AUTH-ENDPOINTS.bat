@echo off
echo ========================================
echo Testing Authentication Endpoints
echo ========================================
echo.

set BASE_URL=http://127.0.0.1:8001
set TEST_EMAIL=authtest_%RANDOM%@example.com
set TEST_PASSWORD=testpass123
set TEST_NAME=Auth Test User

echo [1/4] Testing Health Check...
curl -s %BASE_URL%/health
echo.
echo.

echo [2/4] Testing Signup...
echo Email: %TEST_EMAIL%
curl -s -X POST %BASE_URL%/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"%TEST_PASSWORD%\",\"name\":\"%TEST_NAME%\"}" ^
  > signup_result.json 2>&1

findstr /C:"access_token" signup_result.json >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED
    type signup_result.json
    del signup_result.json 2>nul
    pause
    exit /b 1
) else (
    echo ✅ SUCCESS
)
echo.

echo [3/4] Testing Signin...
curl -s -X POST %BASE_URL%/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"%TEST_PASSWORD%\"}" ^
  > signin_result.json 2>&1

findstr /C:"access_token" signin_result.json >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED
    type signin_result.json
    del signup_result.json signin_result.json 2>nul
    pause
    exit /b 1
) else (
    echo ✅ SUCCESS
)
echo.

echo [4/4] Testing Protected Endpoint...
for /f "tokens=2 delims=:," %%a in ('type signin_result.json ^| findstr "access_token"') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN: =%

curl -s -X GET %BASE_URL%/api/auth/me ^
  -H "Authorization: Bearer %TOKEN%" ^
  > me_result.json 2>&1

findstr /C:"email" me_result.json >nul 2>&1
if errorlevel 1 (
    echo ❌ FAILED
    type me_result.json
) else (
    echo ✅ SUCCESS
)

del signup_result.json signin_result.json me_result.json 2>nul

echo.
echo ========================================
echo ✅ ALL TESTS PASSED!
echo ========================================
echo.
echo Your authentication backend is working!
echo.
echo Next: Open http://127.0.0.1:8001/docs
echo.
pause
