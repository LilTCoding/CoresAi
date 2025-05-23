@echo off
title CoresAI Crypto Trading Backend

echo ========================================
echo    CoresAI Crypto Trading Backend
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r crypto_requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Set environment variables
set ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
set SECRET_KEY=your-secret-key-here-change-in-production
set REDIS_URL=redis://localhost:6379

echo.
echo Starting CoresAI Crypto Trading Backend...
echo Backend will be available at: http://localhost:8082
echo API Documentation: http://localhost:8082/docs
echo.

REM Start the server
python crypto_trading_backend.py

echo.
echo Backend stopped.
pause 