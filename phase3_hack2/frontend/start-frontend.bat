@echo off
echo ========================================
echo Starting Next.js Frontend
echo ========================================
echo.
echo NOTE: If port 3000 is taken, Next.js will use 3001
echo Make sure BETTER_AUTH_URL in .env.local matches the actual port
echo.
cd /d "%~dp0"
npm run dev
