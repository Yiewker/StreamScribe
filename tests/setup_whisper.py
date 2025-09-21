"""
Whisper 环境设置脚本

用于检查和安装 whisper-ctranslate2 到指定的虚拟环境中。
"""

import os
import subprocess
import sys
from pathlib import Path
from core.config import get_config


def check_whisper_installation():
    """检查 Whisper 是否已安装"""
    try:
        config = get_config()
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        if not os.path.exists(python_exe):
            print(f"错误: Whisper 虚拟环境不存在: {config.whisper_venv_path}")
            return False
        
        # 检查是否安装了 whisper-ctranslate2
        result = subprocess.run(
            [python_exe, '-c', 'import whisper_ctranslate2; print("已安装")'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ whisper-ctranslate2 已安装")
            return True
        else:
            print("✗ whisper-ctranslate2 未安装")
            return False
            
    except Exception as e:
        print(f"检查 Whisper 安装时出错: {e}")
        return False


def install_whisper():
    """安装 whisper-ctranslate2"""
    try:
        config = get_config()
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        pip_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'pip.exe')
        
        print("正在安装 whisper-ctranslate2...")
        
        # 安装命令
        install_commands = [
            [pip_exe, 'install', '--upgrade', 'pip'],
            [pip_exe, 'install', 'whisper-ctranslate2[dev]'],
            [pip_exe, 'install', 'torch', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu']
        ]
        
        for cmd in install_commands:
            print(f"执行: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode != 0:
                print(f"安装失败: {result.stderr}")
                return False
            else:
                print("✓ 安装成功")
        
        return True
        
    except Exception as e:
        print(f"安装 Whisper 时出错: {e}")
        return False


def test_whisper():
    """测试 Whisper 功能"""
    try:
        config = get_config()
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        print("测试 Whisper 功能...")
        
        # 测试导入
        result = subprocess.run(
            [python_exe, '-c', '''
import whisper_ctranslate2
print("模块导入成功")
print(f"版本: {whisper_ctranslate2.__version__}")
'''],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Whisper 功能测试通过")
            print(result.stdout)
            return True
        else:
            print("✗ Whisper 功能测试失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"测试 Whisper 时出错: {e}")
        return False


def main():
    """主函数"""
    print("Whisper 环境设置")
    print("=" * 30)
    
    # 检查当前安装状态
    if check_whisper_installation():
        print("\nWhisper 已正确安装，进行功能测试...")
        if test_whisper():
            print("\n✓ 所有检查通过，Whisper 环境就绪！")
            return True
        else:
            print("\n✗ Whisper 功能测试失败，可能需要重新安装")
    
    # 询问是否安装
    print("\n是否要安装/重新安装 whisper-ctranslate2？")
    choice = input("输入 y 继续，其他键退出: ").strip().lower()
    
    if choice != 'y':
        print("退出安装")
        return False
    
    # 执行安装
    if install_whisper():
        print("\n安装完成，进行功能测试...")
        if test_whisper():
            print("\n✓ 安装和测试都成功！Whisper 环境就绪！")
            return True
        else:
            print("\n✗ 安装成功但功能测试失败")
            return False
    else:
        print("\n✗ 安装失败")
        return False


if __name__ == "__main__":
    try:
        success = main()
        input(f"\n{'成功' if success else '失败'}！按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
