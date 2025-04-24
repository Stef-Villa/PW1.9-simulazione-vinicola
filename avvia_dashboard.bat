@echo off
echo Assicurati di aver installato i moduli con: pip install -r requirements.txt
cd /d "%~dp0"
python -m app_dashboard.app
pause