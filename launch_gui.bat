@echo off
cd /d "%~dp0"
python -m smite2db.gui
if errorlevel 1 pause
