#!/usr/bin/env python3
"""
StreamScribe 打包脚本
用于生成绿色版exe文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller 已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("正在安装 PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller 安装失败")
            return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件和资源
datas = [
    ('config.ini', '.'),
    ('config_gpu.ini', '.'),
    ('icon.png', '.'),
    ('docs', 'docs'),
]

# 隐藏导入（确保所有必要模块被包含）
hiddenimports = [
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'configparser',
    'psutil',
    'pathlib',
    'threading',
    'subprocess',
    'logging',
    'datetime',
    'json',
    're',
    'os',
    'sys',
    'time',
    'core',
    'core.config',
    'core.manager',
    'core.transcriber',
    'core.utils',
    'core.platform',
    'core.platform.youtube',
    'core.platform.bilibili',
    'ui_compact',
]

# 排除的模块（减小文件大小）
excludes = [
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'cv2',
    'torch',
    'tensorflow',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StreamScribe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',  # 使用项目图标
)
'''
    
    with open('StreamScribe.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 创建 StreamScribe.spec 文件")

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")
    try:
        # 使用spec文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "StreamScribe.spec"]
        subprocess.check_call(cmd)
        print("✅ exe文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    # 创建发布目录
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制exe文件
    exe_path = Path("dist/StreamScribe.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / "StreamScribe.exe")
        print("✅ 复制exe文件")
    else:
        print("❌ 找不到exe文件")
        return False
    
    # 复制必要的配置文件
    files_to_copy = [
        "config.ini",
        "config_gpu.ini", 
        "README.md",
        "LICENSE",
        "VERSION"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir / file_name)
            print(f"✅ 复制 {file_name}")
    
    # 复制docs目录
    if os.path.exists("docs"):
        shutil.copytree("docs", release_dir / "docs")
        print("✅ 复制 docs 目录")
    
    # 创建启动说明
    readme_content = """# StreamScribe 绿色版

## 使用说明

1. 双击 `StreamScribe.exe` 启动程序
2. 首次运行会自动创建配置文件
3. 根据需要修改 `config.ini` 配置文件
4. 如需GPU加速，可参考 `config_gpu.ini` 配置

## 系统要求

- Windows 10/11 (64位)
- 至少 4GB 内存
- 网络连接（用于下载视频和AI模型）

## 注意事项

- 本程序为绿色版，无需安装，可直接运行
- 首次使用时会自动下载必要的AI模型
- 建议将程序放在有写入权限的目录中

## 更多信息

- 项目主页: https://github.com/Yiewker/StreamScribe
- 问题反馈: https://github.com/Yiewker/StreamScribe/issues
"""
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 创建使用说明")
    
    print(f"📦 发布包创建完成: {release_dir.absolute()}")
    return True

def main():
    """主函数"""
    print("🚀 StreamScribe 打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建exe
    if not build_exe():
        return False
    
    # 创建发布包
    if not create_release_package():
        return False
    
    print("\n🎉 打包完成！")
    print("📁 发布文件位于 'release' 目录中")
    print("💡 可以将整个 'release' 目录打包分发")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
