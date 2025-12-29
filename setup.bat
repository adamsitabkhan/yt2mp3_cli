@echo off
setlocal
echo ===========================================
echo   YouTube to MP3 CLI - Setup (Windows)
echo ===========================================

:: 1. Install Python Libraries
echo [1/2] Installing required Python libraries...
python -m pip install --upgrade pip
python -m pip install yt-dlp mutagen python-dotenv prompt_toolkit

:: 2. Initialize .env file
echo [2/2] Checking for .env file...
if not exist .env (
    echo OUTPUT_FOLDER='' > .env
    echo ✅ Created new .env file with OUTPUT_FOLDER=''
) else (
    echo ✅ .env file already exists.
)

echo.
echo ===========================================
echo   Setup Complete! 
echo   Run your script with: python yt2mp3.py
echo ===========================================
pause