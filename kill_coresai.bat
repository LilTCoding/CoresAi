@echo off
title CoresAI System Shutdown
echo.
echo ========================================
echo     CoresAI System Shutdown
echo ========================================
echo.

REM Kill all Python processes running the backends
echo Stopping backend services...
taskkill /F /FI "WINDOWTITLE eq CoresAI Production Backend*" /T
taskkill /F /FI "WINDOWTITLE eq CoresAI Streaming Backend*" /T
taskkill /F /FI "WINDOWTITLE eq CoresAI Crypto Backend*" /T
taskkill /F /FI "WINDOWTITLE eq CoresAI Discord Bot*" /T

REM Kill the frontend development server
echo Stopping frontend server...
taskkill /F /FI "WINDOWTITLE eq CoresAI Frontend*" /T

REM Kill any remaining Python processes
echo Checking for remaining processes...
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq CoresAI*" /T 2>nul
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq CoresAI*" /T 2>nul

REM Free up ports
echo Freeing up ports...
netstat -ano | findstr :8081 | findstr LISTENING > temp.txt
for /f "tokens=5" %%a in (temp.txt) do taskkill /F /PID %%a 2>nul
netstat -ano | findstr :8082 | findstr LISTENING > temp.txt
for /f "tokens=5" %%a in (temp.txt) do taskkill /F /PID %%a 2>nul
netstat -ano | findstr :8083 | findstr LISTENING > temp.txt
for /f "tokens=5" %%a in (temp.txt) do taskkill /F /PID %%a 2>nul
del temp.txt 2>nul

echo.
echo ========================================
echo CoresAI System has been shut down.
echo All services have been terminated.
echo ========================================
echo.
pause 