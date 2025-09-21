@echo off
title StreamScribe
cd /d "%~dp0"
echo Starting StreamScribe...
python main.py
if errorlevel 1 (
    echo.
    echo Program exited with error. Check the output above.
    echo.
)
pause
