@echo off
title CoresAI Startup
echo.
echo === CoresAI Startup Script ===
echo.

REM Check for Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check for Node.js installation
node --version > nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher
    pause
    exit /b 1
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "src" mkdir src

REM Configure firewall rules if needed
echo Configuring firewall rules...
call cores.bat

REM Start CoresAI
echo Starting CoresAI...
python start_coresai.py

REM If we get here, there was an error
echo.
echo Press any key to exit...
pause > nul 