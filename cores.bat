@echo off
REM Run as Administrator!

REM Open port 8080 for TCP and UDP (AI backend)
netsh advfirewall firewall add rule name="CoresAI Backend 8080 TCP" dir=in action=allow protocol=TCP localport=8080
netsh advfirewall firewall add rule name="CoresAI Backend 8080 UDP" dir=in action=allow protocol=UDP localport=8080

REM Open port 8081 for TCP and UDP (Streaming backend, optional)
netsh advfirewall firewall add rule name="CoresAI Streaming 8081 TCP" dir=in action=allow protocol=TCP localport=8081
netsh advfirewall firewall add rule name="CoresAI Streaming 8081 UDP" dir=in action=allow protocol=UDP localport=8081

REM Allow Python through the firewall (adjust path if needed)
for %%I in (python.exe pythonw.exe) do (
    for %%J in ("%LocalAppData%\Programs\Python\Python313\%%I" "%SystemRoot%\System32\%%I") do (
        if exist %%J netsh advfirewall firewall add rule name="CoresAI Python (%%~nxJ)" dir=in action=allow program="%%J" enable=yes
    )
)

REM Allow Uvicorn through the firewall (if running as a standalone exe)
if exist "%LocalAppData%\Programs\Python\Python313\Scripts\uvicorn.exe" (
    netsh advfirewall firewall add rule name="CoresAI Uvicorn" dir=in action=allow program="%LocalAppData%\Programs\Python\Python313\Scripts\uvicorn.exe" enable=yes
)

echo.
echo Firewall rules for CoresAI ports and Python/Uvicorn have been added!
pause
