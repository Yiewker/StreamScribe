"""
测试完整系统（包括无字幕视频的 whisper-ctranslate2 转录）
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_subtitle_video():
    """测试有字幕的视频"""
    print("测试有字幕的视频...")
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试有字幕的视频
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        print(f"测试 URL: {test_url}")
        print("开始处理...")
        
        def status_callback(message):
            print(f"状态: {message}")
        
        result = manager.process_url(test_url, status_callback)
        
        if result['success']:
            print(f"✓ 有字幕视频处理成功!")
            print(f"  处理方式: {result.get('method', 'unknown')}")
            print(f"  文稿文件: {result['transcript_file']}")
            return True
        else:
            print(f"✗ 有字幕视频处理失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"有字幕视频测试失败: {e}")
        return False


def test_no_subtitle_video():
    """测试无字幕的视频（使用 whisper-ctranslate2）"""
    print("\n测试无字幕的视频...")
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试无字幕的视频
        test_url = "https://www.youtube.com/watch?v=lPVVPQ5vwQo"
        
        print(f"测试 URL: {test_url}")
        print("开始处理（这可能需要几分钟）...")
        
        def status_callback(message):
            print(f"状态: {message}")
        
        result = manager.process_url(test_url, status_callback)
        
        if result['success']:
            print(f"✓ 无字幕视频处理成功!")
            print(f"  处理方式: {result.get('method', 'unknown')}")
            print(f"  文稿文件: {result['transcript_file']}")
            
            # 读取并显示转录结果
            if Path(result['transcript_file']).exists():
                with open(result['transcript_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"转录内容预览: {content[:300]}...")
            
            return True
        else:
            print(f"✗ 无字幕视频处理失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"无字幕视频测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_whisper_ctranslate2_direct():
    """直接测试 whisper-ctranslate2 可执行文件"""
    print("\n直接测试 whisper-ctranslate2...")
    
    try:
        from core.config import get_config
        import os
        
        config = get_config()
        
        whisper_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'whisper-ctranslate2.exe')
        
        if os.path.exists(whisper_exe):
            print(f"✓ whisper-ctranslate2.exe 存在: {whisper_exe}")
            
            # 测试帮助信息
            import subprocess
            result = subprocess.run(
                [whisper_exe, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✓ whisper-ctranslate2 可以正常调用")
                return True
            else:
                print("✗ whisper-ctranslate2 调用失败")
                return False
        else:
            print(f"✗ whisper-ctranslate2.exe 不存在: {whisper_exe}")
            return False
            
    except Exception as e:
        print(f"直接测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("完整系统测试")
    print("=" * 40)
    
    # 首先测试 whisper-ctranslate2 是否可用
    if not test_whisper_ctranslate2_direct():
        print("✗ whisper-ctranslate2 不可用，无法继续测试")
        return False
    
    # 测试有字幕的视频（快速）
    if not test_subtitle_video():
        print("✗ 有字幕视频测试失败")
        return False
    
    # 询问是否测试无字幕视频（耗时）
    print("\n" + "="*50)
    print("接下来将测试无字幕视频的 AI 转录功能")
    print("这个过程可能需要几分钟时间")
    choice = input("是否继续测试无字幕视频？(y/n): ").strip().lower()
    
    if choice == 'y':
        if test_no_subtitle_video():
            print("\n✓ 所有测试通过！系统完全正常")
            return True
        else:
            print("\n✗ 无字幕视频测试失败")
            return False
    else:
        print("\n✓ 基本功能测试通过！")
        print("（跳过了无字幕视频测试）")
        return True


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
