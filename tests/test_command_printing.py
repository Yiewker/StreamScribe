"""
测试命令打印功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_command_printing():
    """测试命令打印功能"""
    print("测试命令打印功能...")
    print("=" * 50)
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试有字幕的视频（会打印字幕相关命令）
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        print(f"测试 URL: {test_url}")
        print("开始处理，注意观察打印的命令...")
        print()
        
        def status_callback(message):
            print(f"状态: {message}")
        
        result = manager.process_url(test_url, status_callback)
        
        if result['success']:
            print(f"\n✅ 处理成功!")
            print(f"处理方式: {result.get('method', 'unknown')}")
            print(f"文稿文件: {result['transcript_file']}")
            
            print(f"\n📝 现在你可以:")
            print(f"1. 复制上面打印的 yt-dlp 命令到命令行测试")
            print(f"2. 修改参数进行实验")
            print(f"3. 查看详细的执行过程")
            
            return True
        else:
            print(f"\n❌ 处理失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_no_subtitle_video():
    """测试无字幕视频（会打印 whisper 命令）"""
    print("\n" + "="*50)
    print("测试无字幕视频（whisper 命令打印）")
    print("="*50)
    
    choice = input("是否测试无字幕视频的命令打印？(y/n): ").strip().lower()
    
    if choice != 'y':
        print("跳过无字幕视频测试")
        return True
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试无字幕的视频
        test_url = "https://www.youtube.com/watch?v=lPVVPQ5vwQo"
        
        print(f"测试 URL: {test_url}")
        print("开始处理，注意观察打印的命令...")
        print()
        
        def status_callback(message):
            print(f"状态: {message}")
        
        result = manager.process_url(test_url, status_callback)
        
        if result['success']:
            print(f"\n✅ 处理成功!")
            print(f"处理方式: {result.get('method', 'unknown')}")
            print(f"文稿文件: {result['transcript_file']}")
            
            print(f"\n📝 现在你可以:")
            print(f"1. 复制上面打印的 yt-dlp 和 whisper-ctranslate2 命令")
            print(f"2. 在命令行中单独测试这些命令")
            print(f"3. 调整参数进行性能优化实验")
            
            return True
        else:
            print(f"\n❌ 处理失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🔍 命令打印功能测试")
    print("=" * 60)
    print("这个测试会显示所有执行的 yt-dlp 和 whisper-ctranslate2 命令")
    print("你可以复制这些命令到命令行中单独测试")
    print("=" * 60)
    
    # 测试有字幕视频
    if not test_command_printing():
        print("❌ 有字幕视频测试失败")
        return False
    
    # 测试无字幕视频
    if not test_no_subtitle_video():
        print("❌ 无字幕视频测试失败")
        return False
    
    print("\n" + "="*60)
    print("🎉 命令打印功能测试完成！")
    print("现在所有的 yt-dlp 和 whisper-ctranslate2 命令都会在执行前打印出来")
    print("你可以复制这些命令进行独立测试和调优")
    print("="*60)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        input(f"\n{'测试完成' if success else '测试失败'}！按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
