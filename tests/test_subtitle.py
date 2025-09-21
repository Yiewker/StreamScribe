"""
字幕检测测试脚本

专门测试字幕检测和选择功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_subtitle_detection():
    """测试字幕检测功能"""
    print("测试字幕检测功能...")
    
    try:
        from core.platform.youtube import YouTubeHandler
        
        handler = YouTubeHandler()
        
        # 测试视频 URL（你提到的有中文简体字幕的视频）
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        print(f"测试 URL: {test_url}")
        print("正在检查字幕...")
        
        # 检查字幕
        best_subtitle = handler._check_subtitles(test_url)
        
        if best_subtitle:
            print(f"✓ 检测到字幕: {best_subtitle}")
            return True
        else:
            print("✗ 未检测到字幕")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_video_info():
    """测试视频信息获取"""
    print("\n测试视频信息获取...")
    
    try:
        from core.platform.youtube import YouTubeHandler
        
        handler = YouTubeHandler()
        
        test_url = "https://www.youtube.com/watch?v=8njmQDPHRZI"
        
        print(f"测试 URL: {test_url}")
        print("正在获取视频信息...")
        
        video_info = handler._get_video_info(test_url)
        
        print(f"✓ 视频标题: {video_info.get('title', 'Unknown')}")
        print(f"✓ 视频时长: {video_info.get('duration', 'Unknown')} 秒")
        print(f"✓ 上传者: {video_info.get('uploader', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("字幕检测功能测试")
    print("=" * 30)
    
    tests = [
        test_video_info,
        test_subtitle_detection
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
