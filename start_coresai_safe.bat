@echo off
title CoresAI - Advanced AI Assistant
echo.
echo Starting CoresAI Advanced AI Assistant...
echo.

REM Start the backend server
echo Starting backend server on port 8082...
start "CoresAI Backend" cmd /c "uvicorn crypto_trading_backend:app --host 0.0.0.0 --port 8082 --reload"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

REM Start the frontend
echo Starting React frontend...
cd frontend
start "CoresAI Frontend" cmd /c "npm start"

echo.
echo CoresAI is now running!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8082
echo API Documentation: http://localhost:8082/docs
echo.
echo Press any key to close this window (services will continue running)...
pause > nul 