"""
简单测试脚本

测试基本的 yt-dlp 功能和字幕检测。
"""

import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ytdlp_basic():
    """测试 yt-dlp 基本功能"""
    print("测试 yt-dlp 基本功能...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        # 测试版本
        result = subprocess.run(
            [config.yt_dlp_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✓ yt-dlp 版本: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ yt-dlp 测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_ytdlp_list_subs():
    """测试 yt-dlp 字幕列表功能"""
    print("\n测试 yt-dlp 字幕列表功能...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        command = [config.yt_dlp_path, '--list-subs', test_url]
        
        # 添加代理
        if config.proxy:
            command.extend(['--proxy', config.proxy])
        
        print(f"执行命令: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=False,  # 使用字节模式
            timeout=30
        )
        
        if result.returncode == 0:
            # 尝试解码输出
            output_text = None
            for encoding in ['utf-8', 'gbk', 'cp936', 'latin1']:
                try:
                    output_text = result.stdout.decode(encoding)
                    print(f"✓ 使用编码 {encoding} 成功解码")
                    break
                except UnicodeDecodeError:
                    continue
            
            if output_text:
                print("字幕列表输出:")
                print("-" * 50)
                # 只显示前1000个字符
                print(output_text[:1000])
                if len(output_text) > 1000:
                    print("... (输出被截断)")
                print("-" * 50)
                return True
            else:
                print("✗ 无法解码输出")
                return False
        else:
            print(f"✗ 命令执行失败，返回码: {result.returncode}")
            # 尝试解码错误信息
            try:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                print(f"错误信息: {error_msg}")
            except:
                print("无法解码错误信息")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ 命令执行超时")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("简单功能测试")
    print("=" * 30)
    
    tests = [
        test_ytdlp_basic,
        test_ytdlp_list_subs
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！✓")
    else:
        print("部分测试失败！✗")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
