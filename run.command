#!/bin/bash
# Double-click launcher (macOS / Linux) for Podcast Studio.
# Creates a virtual environment, installs dependencies, and starts the app.
cd "$(dirname "$0")" || exit 1

echo "=============================================="
echo " Podcast Studio - Daily Lesson Recapper"
echo "=============================================="
echo

PY="$(command -v python3 || command -v python)"
if [ -z "$PY" ]; then
    echo "ERROR: Python 3 not found. Install it from https://www.python.org/downloads/"
    read -r -p "Press Enter to close..."; exit 1
fi

VER="$("$PY" -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
if ! "$PY" -c 'import sys;sys.exit(0 if sys.version_info>=(3,10) else 1)'; then
    echo "ERROR: Python 3.10 or newer is required (you have $VER)."
    echo "Install a newer Python from https://www.python.org/downloads/ and try again."
    read -r -p "Press Enter to close..."; exit 1
fi

if [ ! -d .venv ]; then
    echo "First-time setup: creating the virtual environment (this happens once)..."
    "$PY" -m venv .venv || { echo "Failed to create venv."; read -r -p "Press Enter..."; exit 1; }
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo "Installing / checking dependencies..."
pip install -q --disable-pip-version-check -r requirements.txt

if [ ! -f .env ]; then
    echo
    echo "ERROR: no .env file found."
    echo "Copy .env.example to .env and paste your own OpenAI API key into it, then run again."
    read -r -p "Press Enter to close..."; exit 1
fi

echo
echo "Starting the app... open http://localhost:7860 in your browser."
echo "(Press Ctrl+C in this window to stop.)"
python src/main.py
