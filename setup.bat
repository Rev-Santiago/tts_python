@echo off
TITLE TTS Streaming Server
echo Starting TTS Streaming Server...

REM Navigate to the directory where this .bat file is located
cd /d "%~dp0"

REM Check for virtual environment and activate it
if exist .venv\Scripts\activate (
    echo Exsit .venv...
) else if exist venv\Scripts\activate (
    echo Exist venv...
) else (
    python -m venv venv
    pause
    exit /b
)

call venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt