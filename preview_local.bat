@echo off
cd /d "%~dp0"
echo Refreshing metrics + web export...
python -m smite2db.refresh
if errorlevel 1 (
  echo Refresh failed. Is the venv active / deps installed?
  pause
  exit /b 1
)
echo.
echo Starting local server at http://localhost:8080/
echo Open that URL (or /standalone.html). Ctrl+C to stop.
cd docs
python -m http.server 8080
