@echo off
echo 🚀 CoresAI Frontend - Vercel Deployment Script
echo ================================================
echo.

echo 📋 Checking prerequisites...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ npm is not installed or not in PATH
    echo Please install npm or use Node.js installer
    pause
    exit /b 1
)

echo ✅ Node.js and npm are available

echo.
echo 📦 Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed
)

echo.
echo 🔧 Building the React application...
npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Build completed successfully

echo.
echo 🌐 Checking for Vercel CLI...
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Vercel CLI globally...
    npm install -g vercel
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install Vercel CLI
        echo You can install it manually with: npm install -g vercel
        pause
        exit /b 1
    )
)

echo ✅ Vercel CLI is available

echo.
echo 🚀 Deploying to Vercel...
echo.
echo Choose deployment type:
echo 1. Development/Preview deployment
echo 2. Production deployment
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo Deploying to preview environment...
    vercel
) else if "%choice%"=="2" (
    echo Deploying to production...
    vercel --prod
) else (
    echo Invalid choice. Deploying to preview environment...
    vercel
)

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deployment failed
    echo.
    echo Common issues:
    echo - Make sure you're logged in to Vercel: vercel login
    echo - Check your internet connection
    echo - Verify your project configuration
    pause
    exit /b 1
)

echo.
echo ✅ Deployment completed successfully!
echo.
echo 📋 Next steps:
echo 1. Check your Vercel dashboard for deployment details
echo 2. Update your backend CORS settings to allow your Vercel domain
echo 3. Configure environment variables in Vercel dashboard:
echo    - REACT_APP_PRODUCTION_API_URL
echo    - REACT_APP_STREAMING_API_URL
echo.
echo 🔧 Don't forget to update your backend URLs for production!
echo.
pause 