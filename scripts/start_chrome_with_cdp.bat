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

REM QUAN TRONG: phai dung --user-data-dir rieng, khac voi profile Chrome
REM binh thuong dang mo. Neu Chrome da chay san (voi profile mac dinh),
REM Windows se chi mo them 1 tab trong tien trinh do va BO QUA flag
REM --remote-debugging-port, khien CDP khong bao gio bat len duoc.
set "CDP_PROFILE_DIR=%TEMP%\chrome-cdp-profile"

start "" "%CHROME_PATH%" --remote-debugging-port=%PORT% --user-data-dir="%CDP_PROFILE_DIR%" --no-first-run --no-default-browser-check

echo [OK] Chrome da duoc khoi dong voi CDP (profile rieng: %CDP_PROFILE_DIR%)
echo.
echo Doi vai giay roi kiem tra CDP bang cach truy cap: http://localhost:%PORT%/json
echo Hoac chay: curl http://localhost:%PORT%/json
echo.
echo Neu van khong ket noi duoc: dong TOAN BO cua so Chrome dang mo roi chay lai script nay.
