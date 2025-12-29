@echo off
REM Script để khởi động Chrome với CDP trên Windows

set PORT=%1
if "%PORT%"=="" set PORT=9223

REM Tạo thư mục user data riêng cho CDP
set USER_DATA_DIR=C:\temp\chrome-cdp-profile
if not exist "%USER_DATA_DIR%" mkdir "%USER_DATA_DIR%"

echo Khởi động Chrome với CDP tại port %PORT%...
echo URL endpoint: http://localhost:%PORT%
echo User data directory: %USER_DATA_DIR%
echo.

REM Tìm đường dẫn Chrome (thử các vị trí phổ biến)
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else (
    echo ❌ Không tìm thấy Chrome. Vui lòng chỉ định đường dẫn thủ công.
    echo.
    echo Cú pháp:
    echo "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=%PORT% --user-data-dir="%USER_DATA_DIR%"
    exit /b 1
)

start "" "%CHROME_PATH%" --remote-debugging-port=%PORT% --user-data-dir="%USER_DATA_DIR%" --no-first-run --no-default-browser-check

echo ✓ Chrome đã được khởi động với CDP
echo.
echo Kiểm tra CDP bằng cách truy cập: http://localhost:%PORT%/json
echo Hoặc chạy: curl http://localhost:%PORT%/json
