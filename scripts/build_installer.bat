@echo off
REM Build script: Build executable + tạo installer
REM Usage: scripts\build_installer.bat

echo ==========================================
echo Building Etsy Crawler (Windows)
echo ==========================================
echo.

REM Check if pyinstaller is installed
where pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller chua duoc cai dat!
    echo    Chay: pip install pyinstaller
    exit /b 1
)

REM Check if Inno Setup is installed
set "INNO_SETUP=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_SETUP%" (
    echo [ERROR] Inno Setup khong tim thay tai: %INNO_SETUP%
    echo    Vui long cai Inno Setup tu: https://jrsoftware.org/isdl.php
    exit /b 1
)

REM Clean previous builds
echo [INFO] Dang xoa build cu...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build PyInstaller executable
echo [INFO] Dang build PyInstaller executable...
pyinstaller build.spec
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build that bai!
    exit /b 1
)

REM Build installer
echo [INFO] Dang build Windows installer...
"%INNO_SETUP%" installer\windows\EtsyCrawler.iss
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Inno Setup build that bai!
    exit /b 1
)

echo.
echo [SUCCESS] Build hoan tat!
echo    Executable: dist\EtsyCrawler.exe
echo    Installer: installer\windows\output\EtsyCrawler-Setup-*.exe
echo.

