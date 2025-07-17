@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo Installing Playwright browsers...
playwright install chromium

echo Starting FastAPI server...
python src/app/server.py

pause 