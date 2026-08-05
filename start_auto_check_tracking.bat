@echo off

REM Kich hoat venv - uu tien .venv (theo docs/DEPLOY_WINDOWS.md), fallback venv neu co
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Khong tim thay virtualenv (.venv hoac venv). Tao truoc bang:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Chay API server
python src\app\api_server.py

pause