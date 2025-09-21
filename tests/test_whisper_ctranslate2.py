"""
测试 whisper-ctranslate2 的正确调用方式
"""

import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_whisper_ctranslate2_exe():
    """测试 whisper-ctranslate2 可执行文件"""
    print("测试 whisper-ctranslate2 可执行文件...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        # 检查可执行文件
        whisper_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'whisper-ctranslate2.exe')
        
        if os.path.exists(whisper_exe):
            print(f"✓ whisper-ctranslate2.exe 存在: {whisper_exe}")
        else:
            print(f"✗ whisper-ctranslate2.exe 不存在: {whisper_exe}")
            
            # 列出 Scripts 目录中的文件
            scripts_dir = os.path.join(config.whisper_venv_path, 'Scripts')
            if os.path.exists(scripts_dir):
                files = [f for f in os.listdir(scripts_dir) if 'whisper' in f.lower()]
                print(f"Scripts 目录中的 whisper 相关文件: {files}")
            
            return False
        
        # 测试版本
        result = subprocess.run(
            [whisper_exe, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ whisper-ctranslate2 版本: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ 无法获取版本: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_whisper_ctranslate2_with_file():
    """测试 whisper-ctranslate2 处理音频文件"""
    print("\n测试 whisper-ctranslate2 处理音频文件...")
    
    # 使用你提到的测试文件
    test_file = r"J:\Users\ccd\Downloads\temp\test1.mp3"
    
    if not os.path.exists(test_file):
        print(f"✗ 测试文件不存在: {test_file}")
        print("请确保测试文件存在")
        return False
    
    print(f"✓ 测试文件存在: {test_file}")
    
    try:
        from core.config import get_config
        config = get_config()
        
        whisper_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'whisper-ctranslate2.exe')
        
        # 构建命令（模仿你在 cmd 中使用的命令）
        command = [
            whisper_exe,
            test_file,
            '--model', 'small',
            '--language', 'Chinese',
            '--output_format', 'txt',
            '--output_dir', config.output_dir
        ]
        
        print(f"执行命令: {' '.join(command)}")
        
        # 执行命令
        result = subprocess.run(
            command,
            capture_output=True,
            text=False,  # 使用字节模式避免编码问题
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("✓ whisper-ctranslate2 执行成功")
            
            # 尝试解码输出
            try:
                output = result.stdout.decode('utf-8', errors='ignore')
                print(f"输出: {output[:500]}...")
            except:
                try:
                    output = result.stdout.decode('gbk', errors='ignore')
                    print(f"输出: {output[:500]}...")
                except:
                    print("无法解码输出")
            
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
            print("✗ whisper-ctranslate2 执行失败")
            
            # 尝试解码错误信息
            try:
                error = result.stderr.decode('utf-8', errors='ignore')
                print(f"错误: {error}")
            except:
                try:
                    error = result.stderr.decode('gbk', errors='ignore')
                    print(f"错误: {error}")
                except:
                    print("无法解码错误信息")
            
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ whisper-ctranslate2 执行超时")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_transcriber_updated():
    """测试更新后的转录器"""
    print("\n测试更新后的转录器...")
    
    try:
        from core.transcriber import WhisperTranscriber
        
        transcriber = WhisperTranscriber()
        
        # 测试音频文件
        test_file = r"J:\Users\ccd\Downloads\temp\test1.mp3"
        
        if not os.path.exists(test_file):
            print(f"✗ 测试文件不存在: {test_file}")
            return False
        
        print(f"✓ 测试文件存在: {test_file}")
        print("开始转录测试...")
        
        # 执行转录
        result_file = transcriber.run_whisper(test_file)
        
        if result_file and os.path.exists(result_file):
            print(f"✓ 转录成功，结果文件: {result_file}")
            
            # 读取并显示结果
            with open(result_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"转录内容预览: {content[:200]}...")
            
            return True
        else:
            print("✗ 转录失败，未找到结果文件")
            return False
            
    except Exception as e:
        print(f"转录器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("whisper-ctranslate2 功能测试")
    print("=" * 40)
    
    tests = [
        test_whisper_ctranslate2_exe,
        test_whisper_ctranslate2_with_file,
        test_transcriber_updated
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试 {test.__name__} 失败")
            break
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ whisper-ctranslate2 功能正常！")
        return True
    else:
        print("✗ whisper-ctranslate2 功能存在问题")
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
