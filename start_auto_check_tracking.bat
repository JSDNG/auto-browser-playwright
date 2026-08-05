@echo off

REM Kich hoat venv: uu tien .venv, fallback venv
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
if not defined VIRTUAL_ENV if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
if not defined VIRTUAL_ENV (
    echo [ERROR] Khong tim thay .venv hoac venv. Chay: python -m venv .venv
    exit /b 1
)

python src\app\api_server.py
pause
