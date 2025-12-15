@echo off
REM Windows setup script for Playwright Backend Service
REM Steps: create venv, install deps, install Playwright browser

setlocal enabledelayedexpansion

REM Move to repo root (one level up from scripts folder)
pushd "%~dp0.."

REM Pick Python executable (prioritize python, fall back to py)
set "PYTHON=python"
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    set "PYTHON=py"
)

REM Check Python availability
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11+ is required. Please install it then rerun this script.
    popd
    exit /b 1
)

echo [INFO] Using Python executable: %PYTHON%

REM Create virtual environment if missing
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        popd
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment already exists.
)

REM Activate virtual environment
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    popd
    exit /b 1
)

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Pip upgrade failed.
    popd
    exit /b 1
)

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    popd
    exit /b 1
)

REM Install Playwright Chromium browser
echo [INFO] Installing Playwright Chromium (headless)...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERROR] Playwright browser install failed.
    popd
    exit /b 1
)

REM Create .env from template if missing
if not exist ".env" (
    if exist ".env-example" (
        echo [INFO] Creating .env from .env-example...
        copy ".env-example" ".env" >nul
    )
)

echo.
echo [SUCCESS] Setup completed.
echo Next steps:
echo   1. Start Chrome with CDP: scripts\start_chrome_with_cdp.bat
echo   2. Activate venv (if not active): venv\Scripts\activate
echo   3. Run API server: uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5000
echo   4. Open docs: http://localhost:5000/docs

popd
exit /b 0
