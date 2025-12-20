@echo off

REM kích hoạt venv (đúng tên: venv)
call venv\Scripts\activate

REM chạy API server
python src\app\api_server.py

pause