@echo off
REM Script để khởi động Chrome với HideMyAcc profile qua CDP trên Windows

set PORT=%1
set PROFILE_ID=%2

if "%PORT%"=="" set PORT=9222
if "%PROFILE_ID%"=="" (
    echo ❌ Thiếu tham số PROFILE_ID
    echo.
    echo Cú pháp:
    echo   %0 [PORT] [PROFILE_ID]
    echo.
    echo Ví dụ:
    echo   %0 9222 profile1
    echo.
    echo Để xem danh sách profiles, chạy:
    echo   python3 -m src.utils.hidemyacc
    exit /b 1
)

REM Tìm Chrome path
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else (
    echo ❌ Không tìm thấy Chrome
    exit /b 1
)

echo Đang tìm HideMyAcc profile: %PROFILE_ID%...
python3 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.').absolute().parent)); from src.utils.hidemyacc import HideMyAccManager; manager = HideMyAccManager(); profile = manager.get_profile_by_id('%PROFILE_ID%'); print(profile['user_data_dir'] if profile else 'NOT_FOUND')" > temp_profile_path.txt
set /p PROFILE_PATH=<temp_profile_path.txt
del temp_profile_path.txt

if "%PROFILE_PATH%"=="NOT_FOUND" (
    echo ❌ Không tìm thấy profile: %PROFILE_ID%
    echo.
    echo Danh sách profiles có sẵn:
    python3 -m src.utils.hidemyacc
    exit /b 1
)

echo ✓ Tìm thấy profile tại: %PROFILE_PATH%
echo.
echo Khởi động Chrome với HideMyAcc profile qua CDP...
echo Port: %PORT%
echo Profile: %PROFILE_ID%
echo.

start "" "%CHROME_PATH%" --remote-debugging-port=%PORT% --user-data-dir="%PROFILE_PATH%" --no-first-run --no-default-browser-check --disable-blink-features=AutomationControlled --disable-infobars

echo ✓ Chrome đã được khởi động
echo.
echo CDP endpoint: http://localhost:%PORT%
echo Kiểm tra: curl http://localhost:%PORT%/json
