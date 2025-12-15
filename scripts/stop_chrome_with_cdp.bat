@echo off
REM Script để dừng Chrome đang chạy với CDP trên Windows

set PORT=%1
if "%PORT%"=="" set PORT=9222

echo Đang tìm Chrome đang chạy với CDP tại port %PORT%...
echo.

REM Tìm process Chrome với remote-debugging-port
REM Sử dụng wmic để tìm process và command line
for /f "tokens=2" %%i in ('wmic process where "name='chrome.exe'" get ProcessId,CommandLine /format:list ^| findstr /i "remote-debugging-port=%PORT%" ^| findstr "ProcessId="') do (
    set PID=%%i
    echo Tìm thấy Chrome process với CDP: PID=%%i
    echo Đang dừng process %%i...
    taskkill /PID %%i /F >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Không thể dừng process %%i
    ) else (
        echo ✓ Đã dừng process %%i
    )
)

REM Kiểm tra lại bằng cách thử kết nối đến CDP
echo.
echo Kiểm tra CDP đã tắt...
curl -s http://localhost:%PORT%/json >nul 2>&1
if errorlevel 1 (
    echo ✓ CDP đã tắt tại port %PORT%
) else (
    echo ⚠️  CDP vẫn còn hoạt động tại http://localhost:%PORT%
    echo    Có thể cần đợi thêm vài giây hoặc có Chrome instance khác đang chạy
)

echo.
echo Hoàn tất!
