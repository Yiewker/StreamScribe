"""
修复后的字幕检测测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_subtitle_detection_fixed():
    """测试修复后的字幕检测功能"""
    print("测试修复后的字幕检测功能...")
    
    try:
        from core.platform.youtube import YouTubeHandler
        
        handler = YouTubeHandler()
        
        # 测试视频 URL
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        print(f"测试 URL: {test_url}")
        print("正在检查字幕...")
        
        # 检查字幕
        best_subtitle = handler._check_subtitles(test_url)
        
        if best_subtitle:
            print(f"✓ 检测到最佳字幕: {best_subtitle}")
            
            # 测试字幕优先级选择
            print("\n测试字幕优先级选择...")
            test_subs = ['en', 'zh-Hans', 'zh-Hant', 'fr', 'de']
            selected = handler._select_best_subtitle(test_subs)
            print(f"从 {test_subs} 中选择: {selected}")
            
            return True
        else:
            print("✗ 未检测到字幕")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_process():
    """测试完整的处理流程"""
    print("\n测试完整的处理流程...")
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        print(f"测试 URL: {test_url}")
        print("开始处理...")
        
        def status_callback(message):
            print(f"状态: {message}")
        
        # 处理视频
        result = manager.process_url(test_url, status_callback)
        
        if result['success']:
            print(f"✓ 处理成功!")
            print(f"  平台: {result['platform']}")
            print(f"  视频标题: {result['video_title']}")
            print(f"  处理方式: {result.get('method', 'unknown')}")
            print(f"  文稿文件: {result['transcript_file']}")
            return True
        else:
            print(f"✗ 处理失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("修复后的字幕检测测试")
    print("=" * 40)
    
    # 只测试字幕检测，不进行完整处理（避免下载大文件）
    tests = [
        test_subtitle_detection_fixed,
        # test_full_process  # 注释掉完整测试，避免实际下载
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("所有测试通过！✓")
        print("\n如果要测试完整流程（包括实际下载），请取消注释 test_full_process")
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
