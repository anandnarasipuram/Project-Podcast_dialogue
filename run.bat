@echo off
REM Double-click launcher (Windows) for Podcast Studio.
REM Creates a virtual environment, installs dependencies, and starts the app.
cd /d "%~dp0"

echo ==============================================
echo  Podcast Studio - Daily Lesson Recapper
echo ==============================================
echo.

where python >nul 2>&1
if not %errorlevel%==0 (
    echo ERROR: Python not found. Install it from https://www.python.org/downloads/
    echo During install, tick "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('python -c "import sys;print(1 if sys.version_info>=(3,10) else 0)"') do set PYOK=%%v
if "%PYOK%"=="0" (
    echo ERROR: Python 3.10 or newer is required.
    echo Install a newer Python from https://www.python.org/downloads/ and try again.
    echo.
    pause
    exit /b 1
)

if not exist .venv (
    echo First-time setup: creating the virtual environment ^(this happens once^)...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo Installing / checking dependencies...
pip install -q --disable-pip-version-check -r requirements.txt

if not exist .env (
    echo.
    echo ERROR: no .env file found.
    echo Copy .env.example to .env and paste your own OpenAI API key into it, then run again.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting the app... open http://localhost:7860 in your browser.
echo ^(Press Ctrl+C in this window to stop.^)
python src\main.py
