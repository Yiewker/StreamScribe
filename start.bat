@echo off
title StreamScribe Launcher

echo.
echo ========================================
echo   StreamScribe - Video Transcript Tool
echo ========================================
echo.

REM Switch to script directory
cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Check if Python is available
echo Checking Python environment...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found!
    echo Please make sure Python is installed and added to PATH
    echo.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo.
    echo [ERROR] main.py file not found!
    echo Please make sure you are running this script in the correct directory
    echo.
    pause
    exit /b 1
)

REM Start the program
echo.
echo Starting StreamScribe GUI...
echo Please wait, the graphical interface will open shortly...
echo.
echo ----------------------------------------

python main.py

echo.
echo ----------------------------------------
echo StreamScribe has exited
echo.
pause
