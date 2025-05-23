@echo off
title CoresAI Vercel Deployment
echo.
echo ========================================
echo     CoresAI Vercel Deployment
echo ========================================
echo.

REM Check for Vercel CLI
vercel --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Vercel CLI is not installed
    echo Installing Vercel CLI...
    npm install -g vercel
)

REM Build frontend
echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..

REM Prepare backend for deployment
echo.
echo Preparing backend for deployment...
if not exist ".vercel" mkdir .vercel

REM Create Vercel project if it doesn't exist
echo.
echo Configuring Vercel project...
vercel link

REM Deploy to Vercel
echo.
echo Deploying to Vercel...
vercel deploy --prod

echo.
echo ========================================
echo Deployment complete! Your app should be live at:
vercel domains ls
echo ========================================
echo.
pause 