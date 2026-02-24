@echo off
TITLE TTS Streaming Server
echo Starting TTS Streaming Server...

REM Navigate to the directory where this .bat file is located
cd /d "%~dp0"

REM Check for virtual environment and activate it
if exist .venv\Scripts\activate (
    echo Activating .venv...
    call .venv\Scripts\activate
) else if exist venv\Scripts\activate (
    echo Activating venv...
    call venv\Scripts\activate
) else (
    echo [ERROR] Virtual environment not found! Please create one first.
    pause
    exit /b
)

REM Start the FastAPI server using the module approach
echo Launching FastAPI on http://0.0.0.0:8010...
python -m app.main

pause