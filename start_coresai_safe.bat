@echo off
title CoresAI System Launcher
echo.
echo ========================================
echo        CoresAI System Launcher
echo ========================================
echo.

REM Check Python installation
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.13 and try again
    pause
    exit /b 1
)

REM Check Node.js installation
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

REM Create and activate virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
pip install -r crypto_requirements.txt

REM Install Node.js dependencies
echo Installing Node.js dependencies...
cd frontend
call npm install
cd ..

REM Start the backends
echo.
echo Starting CoresAI backends...
start "CoresAI Production Backend" cmd /c "call venv\Scripts\activate && python -m uvicorn production_ai_backend:app --host 0.0.0.0 --port 8082"
timeout /t 2 /nobreak > nul
start "CoresAI Streaming Backend" cmd /c "call venv\Scripts\activate && python -m uvicorn streaming_ai_backend:app --host 0.0.0.0 --port 8081"
timeout /t 2 /nobreak > nul
start "CoresAI Crypto Backend" cmd /c "call venv\Scripts\activate && python -m uvicorn crypto_trading_backend:app --host 0.0.0.0 --port 8083"

REM Start the frontend development server
echo.
echo Starting frontend development server...
cd frontend
start "CoresAI Frontend" cmd /c "npm start"
cd ..

REM Start the Discord bot
echo.
echo Starting Discord bot...
start "CoresAI Discord Bot" cmd /c "call venv\Scripts\activate && python run_bot.py"

echo.
echo ========================================
echo CoresAI System is now running!
echo.
echo Endpoints:
echo - Production Backend: http://localhost:8082
echo - Streaming Backend: http://localhost:8081
echo - Crypto Backend: http://localhost:8083
echo - Frontend: http://localhost:3000
echo.
echo Press any key to shut down all services...
pause > nul

REM Cleanup
taskkill /F /FI "WINDOWTITLE eq CoresAI*" /T
echo.
echo CoresAI System has been shut down.
pause 