"""
调试 Whisper 环境问题
"""

import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_whisper_env():
    """详细调试 Whisper 环境"""
    print("详细调试 Whisper 环境...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        print(f"配置的 Whisper 虚拟环境路径: {config.whisper_venv_path}")
        
        # 检查虚拟环境目录
        if os.path.exists(config.whisper_venv_path):
            print(f"✓ 虚拟环境目录存在")
        else:
            print(f"✗ 虚拟环境目录不存在")
            return False
        
        # 检查 Scripts 目录
        scripts_dir = os.path.join(config.whisper_venv_path, 'Scripts')
        if os.path.exists(scripts_dir):
            print(f"✓ Scripts 目录存在: {scripts_dir}")
            
            # 列出 Scripts 目录内容
            try:
                files = os.listdir(scripts_dir)
                print(f"Scripts 目录内容: {files[:10]}...")  # 只显示前10个
            except Exception as e:
                print(f"无法列出 Scripts 目录: {e}")
        else:
            print(f"✗ Scripts 目录不存在: {scripts_dir}")
            return False
        
        # 检查 Python 解释器
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        if os.path.exists(python_exe):
            print(f"✓ Python 解释器存在: {python_exe}")
        else:
            print(f"✗ Python 解释器不存在: {python_exe}")
            return False
        
        # 测试 Python 版本
        try:
            result = subprocess.run(
                [python_exe, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ Python 版本: {result.stdout.strip()}")
            else:
                print(f"✗ 无法获取 Python 版本: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ 执行 Python 版本检查失败: {e}")
            return False
        
        # 测试包导入
        try:
            result = subprocess.run(
                [python_exe, '-c', 'import sys; print("Python 路径:"); [print(p) for p in sys.path[:5]]'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ Python 路径信息:")
                print(result.stdout)
            else:
                print(f"✗ 无法获取 Python 路径: {result.stderr}")
        except Exception as e:
            print(f"✗ 获取 Python 路径失败: {e}")
        
        # 测试 whisper_ctranslate2 导入
        try:
            result = subprocess.run(
                [python_exe, '-c', 'import whisper_ctranslate2; print("whisper_ctranslate2 导入成功")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✓ whisper_ctranslate2 导入成功")
                print(result.stdout)
                return True
            else:
                print(f"✗ whisper_ctranslate2 导入失败")
                print(f"错误: {result.stderr}")
                
                # 尝试列出已安装的包
                print("\n尝试列出已安装的包...")
                pip_result = subprocess.run(
                    [python_exe, '-m', 'pip', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if pip_result.returncode == 0:
                    lines = pip_result.stdout.split('\n')
                    whisper_packages = [line for line in lines if 'whisper' in line.lower()]
                    if whisper_packages:
                        print("找到的 whisper 相关包:")
                        for pkg in whisper_packages:
                            print(f"  {pkg}")
                    else:
                        print("未找到 whisper 相关包")
                else:
                    print(f"无法列出包: {pip_result.stderr}")
                
                return False
        except Exception as e:
            print(f"✗ 测试 whisper_ctranslate2 导入失败: {e}")
            return False
            
    except Exception as e:
        print(f"调试失败: {e}")
        return False


def main():
    """主函数"""
    print("Whisper 环境调试")
    print("=" * 30)
    
    if debug_whisper_env():
        print("\n✓ Whisper 环境调试完成，环境正常")
        return True
    else:
        print("\n✗ Whisper 环境存在问题")
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
