"""
仅测试现有的 Whisper 功能，不进行安装
"""

import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_whisper_env():
    """测试 Whisper 虚拟环境"""
    print("测试 Whisper 虚拟环境...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        if not os.path.exists(python_exe):
            print(f"✗ Python 解释器不存在: {python_exe}")
            return False
        
        print(f"✓ Python 解释器存在: {python_exe}")
        
        # 测试 Python 版本
        result = subprocess.run(
            [python_exe, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ Python 版本: {result.stdout.strip()}")
        else:
            print(f"✗ 无法获取 Python 版本")
            return False
        
        # 测试是否安装了 whisper_ctranslate2
        result = subprocess.run(
            [python_exe, '-c', 'import whisper_ctranslate2; print("whisper_ctranslate2 可用")'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ whisper_ctranslate2 可用")
            return True
        else:
            print(f"✗ whisper_ctranslate2 不可用")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_whisper_with_file():
    """测试 Whisper 处理指定文件"""
    print("\n测试 Whisper 处理音频文件...")
    
    test_file = r"J:\Users\ccd\Downloads\temp\test1.mp3"
    
    if not os.path.exists(test_file):
        print(f"✗ 测试文件不存在: {test_file}")
        print("请确保测试文件存在，或者修改路径")
        return False
    
    print(f"✓ 测试文件存在: {test_file}")
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        # 构建 whisper 命令，使用 small 模型
        command = [
            python_exe,
            '-m', 'whisper_ctranslate2.cli',
            test_file,
            '--model', 'small',  # 使用 small 模型
            '--output_format', 'txt',
            '--output_dir', config.output_dir
        ]
        
        print(f"执行命令: {' '.join(command)}")
        
        # 执行命令
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("✓ Whisper 执行成功")
            if result.stdout:
                print(f"标准输出: {result.stdout}")
            
            # 查找生成的文件
            test_name = Path(test_file).stem
            output_file = os.path.join(config.output_dir, f"{test_name}.txt")
            
            if os.path.exists(output_file):
                print(f"✓ 找到输出文件: {output_file}")
                
                # 读取并显示内容
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"文稿内容预览: {content[:200]}...")
                
                return True
            else:
                print(f"✗ 未找到输出文件: {output_file}")
                return False
        else:
            print("✗ Whisper 执行失败")
            print(f"错误输出: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Whisper 执行超时")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_whisper_models():
    """测试可用的 Whisper 模型"""
    print("\n测试可用的 Whisper 模型...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        # 测试模型列表
        result = subprocess.run(
            [python_exe, '-c', '''
import whisper_ctranslate2
print("可用模型:")
models = ["tiny", "base", "small", "medium", "large"]
for model in models:
    print(f"  {model}")
'''],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ 模型信息:")
            print(result.stdout)
            return True
        else:
            print("✗ 无法获取模型信息")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("Whisper 功能测试（仅测试，不安装）")
    print("=" * 40)
    
    tests = [
        test_whisper_env,
        test_whisper_models,
        test_whisper_with_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试 {test.__name__} 失败，跳过后续测试")
            break
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！Whisper 环境就绪")
        return True
    else:
        print("✗ 部分测试失败")
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
