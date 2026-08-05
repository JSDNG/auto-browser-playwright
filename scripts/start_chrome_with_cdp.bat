@echo off
REM Script de khoi dong Chrome voi CDP tren Windows

set PORT=%1
if "%PORT%"=="" set PORT=9222

echo Khoi dong Chrome voi CDP tai port %PORT%...
echo URL endpoint: http://localhost:%PORT%
echo.

REM Tim duong dan Chrome (thu cac vi tri pho bien)
REM Dung if tung dong don de tranh loi ngoac () trong "Program Files (x86)"
set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not defined CHROME_PATH if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if not defined CHROME_PATH (
    echo [ERROR] Khong tim thay Chrome. Vui long chi dinh duong dan thu cong.
    echo.
    echo Cu phap:
    echo "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=%PORT%
    exit /b 1
)

start "" "%CHROME_PATH%" --remote-debugging-port=%PORT%

echo [OK] Chrome da duoc khoi dong voi CDP
echo.
echo Kiem tra CDP bang cach truy cap: http://localhost:%PORT%/json
echo Hoac chay: curl http://localhost:%PORT%/json
