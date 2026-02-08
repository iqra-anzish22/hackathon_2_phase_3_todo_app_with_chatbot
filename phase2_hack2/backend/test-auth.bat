@echo off
echo ========================================
echo Testing Authentication Endpoints
echo ========================================
echo.

set BASE_URL=http://127.0.0.1:8001
set TEST_EMAIL=testuser_%RANDOM%@example.com
set TEST_PASSWORD=testpass123
set TEST_NAME=Test User

echo Test 1: Health Check
echo ---------------------
curl -s %BASE_URL%/health
echo.
echo.

echo Test 2: Signup (Register New User)
echo ------------------------------------
echo Email: %TEST_EMAIL%
curl -s -X POST %BASE_URL%/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"%TEST_PASSWORD%\",\"name\":\"%TEST_NAME%\"}" ^
  > signup_response.json

type signup_response.json
echo.
echo.

echo Test 3: Signin (Login)
echo ------------------------
curl -s -X POST %BASE_URL%/api/auth/signin ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%TEST_EMAIL%\",\"password\":\"%TEST_PASSWORD%\"}" ^
  > signin_response.json

type signin_response.json
echo.
echo.

echo Test 4: Get Current User (Protected)
echo ---------------------------------------
for /f "tokens=2 delims=:," %%a in ('type signin_response.json ^| findstr "access_token"') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN: =%

curl -s -X GET %BASE_URL%/api/auth/me ^
  -H "Authorization: Bearer %TOKEN%"
echo.
echo.

echo ========================================
echo All Tests Complete!
echo ========================================
echo.
echo Cleanup: Deleting temporary files...
del signup_response.json signin_response.json 2>nul

pause
