@echo off
REM Script de dung Chrome dang chay voi CDP tren Windows

set PORT=%1
if "%PORT%"=="" set PORT=9222

echo Dang tim Chrome dang chay voi CDP tai port %PORT%...
echo.

REM Tim process Chrome voi remote-debugging-port
REM Su dung wmic de tim process va command line
for /f "tokens=2" %%i in ('wmic process where "name='chrome.exe'" get ProcessId,CommandLine /format:list ^| findstr /i "remote-debugging-port=%PORT%" ^| findstr "ProcessId="') do (
    set PID=%%i
    echo Tim thay Chrome process voi CDP: PID=%%i
    echo Dang dung process %%i...
    taskkill /PID %%i /F >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Khong the dung process %%i
    ) else (
        echo [OK] Da dung process %%i
    )
)

REM Kiem tra lai bang cach thu ket noi den CDP
echo.
echo Kiem tra CDP da tat...
curl -s http://localhost:%PORT%/json >nul 2>&1
if errorlevel 1 (
    echo [OK] CDP da tat tai port %PORT%
) else (
    echo [WARN] CDP van con hoat dong tai http://localhost:%PORT%
    echo    Co the can doi them vai giay hoac co Chrome instance khac dang chay
)

echo.
echo Hoan tat!
