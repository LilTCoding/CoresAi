@echo off
chcp 65001 > nul
echo.
echo ===================================================
echo          CoresAI System Startup
echo ===================================================
echo.
echo Production Backend: http://localhost:8080
echo Streaming Backend:  http://localhost:8081
echo GUI Application:    python gui_app.py
echo.
echo Starting backends in separate windows...
echo.

REM Start production backend in new window
start "CoresAI Production" cmd /k "python production_ai_backend.py"

REM Wait 3 seconds for first backend to start
timeout /t 3 > nul

REM Start streaming backend in new window  
start "CoresAI Streaming" cmd /k "python streaming_ai_backend.py"

echo.
echo ===================================================
echo Both backends are starting in separate windows
echo Check the new command windows for status
echo.
echo To start GUI: python gui_app.py
echo To test: open http://localhost:8080/docs
echo ===================================================
echo.
pause 