@echo off
echo Whisper 环境设置
echo ================
echo.

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请确保 Python 已正确安装并添加到 PATH
    pause
    exit /b 1
)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 运行 Whisper 设置脚本
echo 正在运行 Whisper 环境设置...
python setup_whisper.py

echo.
echo 设置完成
pause
