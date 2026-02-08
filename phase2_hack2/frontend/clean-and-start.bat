@echo off
echo Cleaning Next.js cache...
rmdir /s /q .next 2>nul
echo Cache cleaned!
echo.
echo Starting dev server...
npm run dev
