@echo off
REM Script xóa tất cả cache Python trong dự án

echo 🧹 Đang xóa cache Python...

REM Xóa tất cả thư mục __pycache__ (trừ venv)
for /d /r . %%d in (__pycache__) do (
    echo %%d | findstr /v "venv" >nul
    if !errorlevel! equ 0 (
        if exist "%%d" (
            rmdir /s /q "%%d" 2>nul
        )
    )
)

REM Xóa tất cả file .pyc
for /r . %%f in (*.pyc) do (
    echo %%f | findstr /v "venv" >nul
    if !errorlevel! equ 0 (
        if exist "%%f" (
            del /f /q "%%f" 2>nul
        )
    )
)

REM Xóa tất cả file .pyo
for /r . %%f in (*.pyo) do (
    echo %%f | findstr /v "venv" >nul
    if !errorlevel! equ 0 (
        if exist "%%f" (
            del /f /q "%%f" 2>nul
        )
    )
)

echo ✅ Đã xóa xong tất cả cache!
pause

