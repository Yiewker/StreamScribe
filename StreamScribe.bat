@echo off
title StreamScribe
cd /d "%~dp0"

echo.
echo ==========================================
echo    StreamScribe - Video Transcript Tool
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python and add it to PATH
    pause
    exit /b 1
)

REM Check main.py
if not exist "main.py" (
    echo ERROR: main.py not found!
    echo Please run this script in the correct directory
    pause
    exit /b 1
)

echo Starting StreamScribe GUI...
echo.

python main.py

echo.
echo StreamScribe closed.
pause
