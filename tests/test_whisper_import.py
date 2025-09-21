"""
测试 whisper 的正确导入方式
"""

import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_whisper_imports():
    """测试不同的 whisper 导入方式"""
    print("测试不同的 whisper 导入方式...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        # 测试不同的导入方式
        import_tests = [
            'import whisper_ctranslate2',
            'import whisper',
            'import faster_whisper',
            'from whisper_ctranslate2 import cli',
            'import whisper_ctranslate2.cli',
        ]
        
        for test_import in import_tests:
            print(f"\n测试: {test_import}")
            
            result = subprocess.run(
                [python_exe, '-c', f'{test_import}; print("成功导入")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ {test_import} - 成功")
            else:
                print(f"✗ {test_import} - 失败: {result.stderr.strip()}")
        
        # 测试命令行接口
        print(f"\n测试命令行接口...")
        
        cli_tests = [
            [python_exe, '-m', 'whisper_ctranslate2', '--help'],
            [python_exe, '-m', 'whisper_ctranslate2.cli', '--help'],
            [python_exe, '-m', 'whisper', '--help'],
            [python_exe, '-m', 'faster_whisper', '--help'],
        ]
        
        for cli_test in cli_tests:
            print(f"\n测试命令: {' '.join(cli_test)}")
            
            result = subprocess.run(
                cli_test,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ 命令可用")
                # 显示帮助信息的前几行
                help_lines = result.stdout.split('\n')[:5]
                for line in help_lines:
                    if line.strip():
                        print(f"  {line}")
                break
            else:
                print(f"✗ 命令失败: {result.stderr.strip()}")
        
        return True
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_direct_whisper_command():
    """测试直接的 whisper 命令"""
    print("\n\n测试直接的 whisper 命令...")
    
    test_file = r"J:\Users\ccd\Downloads\temp\test1.mp3"
    
    if not os.path.exists(test_file):
        print(f"✗ 测试文件不存在: {test_file}")
        return False
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        # 尝试不同的命令格式
        commands = [
            [python_exe, '-m', 'whisper_ctranslate2', test_file, '--model', 'small', '--output_format', 'txt'],
            [python_exe, '-m', 'faster_whisper', test_file, '--model', 'small'],
        ]
        
        for cmd in commands:
            print(f"\n尝试命令: {' '.join(cmd[:4])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1分钟超时
            )
            
            if result.returncode == 0:
                print(f"✓ 命令执行成功")
                if result.stdout:
                    print(f"输出: {result.stdout[:200]}...")
                return True
            else:
                print(f"✗ 命令失败")
                if result.stderr:
                    print(f"错误: {result.stderr[:200]}...")
        
        return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def main():
    """主函数"""
    print("Whisper 导入和命令测试")
    print("=" * 40)
    
    test_whisper_imports()
    test_direct_whisper_command()


if __name__ == "__main__":
    try:
        main()
        input("\n按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
