@echo off
REM Run as Administrator!

REM Open port 8082 for TCP and UDP (Crypto Trading Backend)
netsh advfirewall firewall add rule name="CoresAI Crypto Backend 8082 TCP" dir=in action=allow protocol=TCP localport=8082
netsh advfirewall firewall add rule name="CoresAI Crypto Backend 8082 UDP" dir=in action=allow protocol=UDP localport=8082

REM Open port 8081 for TCP and UDP (Streaming Backend)
netsh advfirewall firewall add rule name="CoresAI Streaming 8081 TCP" dir=in action=allow protocol=TCP localport=8081
netsh advfirewall firewall add rule name="CoresAI Streaming 8081 UDP" dir=in action=allow protocol=UDP localport=8081

REM Open port 3000 for TCP (Frontend Development)
netsh advfirewall firewall add rule name="CoresAI Frontend 3000 TCP" dir=in action=allow protocol=TCP localport=3000

REM Allow Python through the firewall (adjust path if needed)
for %%I in (python.exe pythonw.exe) do (
    for %%J in ("%LocalAppData%\Programs\Python\Python313\%%I" "%SystemRoot%\System32\%%I") do (
        if exist %%J netsh advfirewall firewall add rule name="CoresAI Python (%%~nxJ)" dir=in action=allow program="%%J" enable=yes
    )
)

REM Allow Node.js through the firewall
for %%I in (node.exe npm.cmd) do (
    for %%J in ("%ProgramFiles%\nodejs\%%I" "%ProgramFiles(x86)%\nodejs\%%I") do (
        if exist %%J netsh advfirewall firewall add rule name="CoresAI Node.js (%%~nxJ)" dir=in action=allow program="%%J" enable=yes
    )
)

REM Allow Uvicorn through the firewall
if exist "%LocalAppData%\Programs\Python\Python313\Scripts\uvicorn.exe" (
    netsh advfirewall firewall add rule name="CoresAI Uvicorn" dir=in action=allow program="%LocalAppData%\Programs\Python\Python313\Scripts\uvicorn.exe" enable=yes
)

echo.
echo Firewall rules for CoresAI have been configured:
echo - Crypto Backend (8082)
echo - Streaming Backend (8081)
echo - Frontend Development Server (3000)
echo - Python, Node.js, and Uvicorn applications
echo.
pause
