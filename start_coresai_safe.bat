@echo off
title CoresAI - Advanced AI Crypto Trading Assistant
echo Starting CoresAI System...

REM Check if Python virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r crypto_requirements.txt
)

REM Start the crypto trading backend
start "CoresAI Crypto Backend" cmd /c "uvicorn crypto_trading_backend:app --host 0.0.0.0 --port 8082 --reload"

REM Wait for backend to start
timeout /t 5 /nobreak

REM Start the streaming backend
start "CoresAI Streaming Backend" cmd /c "uvicorn streaming_ai_backend:app --host 0.0.0.0 --port 8081 --reload"

REM Wait for streaming backend to start
timeout /t 5 /nobreak

REM Start the frontend
cd frontend
start "CoresAI Frontend" cmd /c "npm install & npm start"

echo.
echo CoresAI System Started Successfully!
echo.
echo Services:
echo - Crypto Backend: http://localhost:8082
echo - Streaming Backend: http://localhost:8081
echo - Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul 