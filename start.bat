@echo off
title CoresAI Startup
echo.
echo === CoresAI Startup Script ===
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Install frontend dependencies
echo Installing frontend dependencies...
npm install

REM Start backend server
echo Starting backend server...
start cmd /k "python -m uvicorn src.app:app --host 0.0.0.0 --port 8082 --reload"

REM Start frontend development server
echo Starting frontend server...
start cmd /k "npm start"

echo.
echo CoresAI is starting up...
echo You can close this window once both servers are running.
echo. 