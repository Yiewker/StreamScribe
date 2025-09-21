@echo off
chcp 65001 >nul
echo 🚀 StreamScribe 打包工具
echo ================================

echo 📋 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo 🔨 开始打包...
python build_exe.py

if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo ✅ 打包成功完成！
echo 📁 发布文件位于 'release' 目录
echo.
echo 按任意键退出...
pause >nul
