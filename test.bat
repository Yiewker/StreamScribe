@echo off
title StreamScribe 测试脚本

echo.
echo ========================================
echo      StreamScribe 测试脚本
echo ========================================
echo.

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请确保 Python 已正确安装并添加到 PATH
    pause
    exit /b 1
)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查测试文件是否存在
if not exist "tests\test_core.py" (
    echo [错误] 未找到测试文件！
    echo 请确保 tests 目录存在且包含测试文件
    pause
    exit /b 1
)

REM 运行测试
echo 正在运行核心功能测试...
echo 测试文件位置: tests\test_core.py
echo.

python tests\test_core.py

echo.
echo 测试完成
pause
