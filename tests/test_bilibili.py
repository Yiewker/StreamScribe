"""
测试B站（Bilibili）处理功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_bilibili_config():
    """测试B站配置"""
    print("测试B站配置...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        
        config = get_config()
        
        # 测试BBDown路径配置
        bbdown_path = config.bbdown_path
        print(f"BBDown 路径: {bbdown_path}")
        
        # 测试BBDown相关配置
        quality = config.bbdown_quality
        download_subtitle = config.bbdown_download_subtitle
        download_danmaku = config.bbdown_download_danmaku
        audio_format = config.bbdown_audio_format
        
        print(f"下载质量: {quality}")
        print(f"下载字幕: {download_subtitle}")
        print(f"下载弹幕: {download_danmaku}")
        print(f"音频格式: {audio_format}")
        
        # 检查BBDown文件是否存在
        if os.path.exists(bbdown_path):
            print(f"✅ BBDown 文件存在")
        else:
            print(f"⚠️ BBDown 文件不存在: {bbdown_path}")
        
        print("\n✅ B站配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ B站配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_url_recognition():
    """测试URL识别功能"""
    print("\n测试URL识别功能...")
    print("=" * 50)
    
    try:
        from core.utils import extract_video_id_from_url
        
        # 测试各种URL格式
        test_urls = [
            # YouTube URLs
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "youtube", "dQw4w9WgXcQ"),
            
            # Bilibili URLs
            ("https://www.bilibili.com/video/BV1xx411c7mD", "bilibili", "BV1xx411c7mD"),
            ("https://www.bilibili.com/video/av123456", "bilibili", "av123456"),
            ("https://b23.tv/abc123", "bilibili", "abc123"),
            
            # 无效URLs
            ("https://example.com/video", None, None),
            ("not a url", None, None),
        ]
        
        for url, expected_platform, expected_id in test_urls:
            platform, video_id = extract_video_id_from_url(url)
            
            if platform == expected_platform and video_id == expected_id:
                print(f"✅ {url[:50]}... -> {platform}, {video_id}")
            else:
                print(f"❌ {url[:50]}... -> 期望: {expected_platform}, {expected_id}, 实际: {platform}, {video_id}")
                return False
        
        print("\n✅ URL识别功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ URL识别功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bilibili_handler():
    """测试B站处理器"""
    print("\n测试B站处理器...")
    print("=" * 50)
    
    try:
        from core.platform.bilibili import BilibiliHandler
        
        handler = BilibiliHandler()
        
        # 测试处理器初始化
        print(f"BBDown 路径: {handler.config.bbdown_path}")
        print(f"下载质量: {handler.config.bbdown_quality}")
        print(f"音频格式: {handler.config.bbdown_audio_format}")
        
        # 测试方法存在性
        methods_to_check = [
            '_get_video_info',
            '_try_download_subtitle',
            '_download_audio',
            '_convert_srt_to_txt',
            'get_transcript'
        ]
        
        for method_name in methods_to_check:
            if hasattr(handler, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
                return False
        
        print("\n✅ B站处理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ B站处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_manager_bilibili():
    """测试任务管理器的B站支持"""
    print("\n测试任务管理器B站支持...")
    print("=" * 50)
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试支持的平台
        platforms = manager.get_supported_platforms()
        print(f"支持的平台: {platforms}")
        
        if 'bilibili' not in platforms:
            print("❌ B站平台未注册")
            return False
        
        print("✅ B站平台已注册")
        
        # 测试平台信息获取
        test_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in test_urls:
            info = manager.get_platform_info(url)
            platform = info['platform']
            supported = info['supported']
            
            print(f"URL: {url[:50]}...")
            print(f"  平台: {platform}")
            print(f"  支持: {supported}")
            
            if platform in ['youtube', 'bilibili'] and supported:
                print(f"  ✅ 正确识别")
            else:
                print(f"  ❌ 识别错误")
                return False
        
        print("\n✅ 任务管理器B站支持测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 任务管理器B站支持测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_smart_processing():
    """测试UI智能处理功能"""
    print("\n测试UI智能处理功能...")
    print("=" * 50)
    
    try:
        from ui import StreamScribeUI
        
        # 创建UI实例（不运行mainloop）
        app = StreamScribeUI()
        
        # 测试URL支持检查
        test_urls = [
            ("https://www.youtube.com/watch?v=test", True),
            ("https://youtu.be/test", True),
            ("https://www.bilibili.com/video/BV123", True),
            ("https://b23.tv/abc", True),
            ("https://example.com/video", False),
        ]
        
        for url, expected in test_urls:
            result = app._is_supported_url(url)
            if result == expected:
                print(f"✅ {url[:40]}... -> {result}")
            else:
                print(f"❌ {url[:40]}... -> 期望: {expected}, 实际: {result}")
                return False
        
        # 测试混合URL解析
        mixed_urls_text = """
        https://www.youtube.com/watch?v=test1
        https://www.bilibili.com/video/BV123
        https://youtu.be/test2
        https://b23.tv/abc
        https://example.com/invalid
        """
        
        parsed_urls = app._parse_urls(mixed_urls_text)
        print(f"\n解析的URL数量: {len(parsed_urls)}")
        
        if len(parsed_urls) == 4:  # 应该过滤掉无效的URL
            print("✅ 混合URL解析正确")
        else:
            print(f"❌ 混合URL解析错误，期望4个，实际{len(parsed_urls)}个")
            return False
        
        # 测试平台识别
        for url in parsed_urls:
            platform = app._get_url_platform(url)
            print(f"  {url[:40]}... -> {platform}")
        
        # 销毁窗口
        app.root.destroy()
        
        print("\n✅ UI智能处理功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ UI智能处理功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🔧 B站（Bilibili）功能测试")
    print("=" * 60)
    
    tests = [
        test_bilibili_config,
        test_url_recognition,
        test_bilibili_handler,
        test_task_manager_bilibili,
        test_ui_smart_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试 {test.__name__} 失败")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有功能测试通过！")
        print("新功能包括:")
        print("✅ B站链接支持（BV号、av号、短链接）")
        print("✅ 智能平台识别（YouTube、B站、本地文件）")
        print("✅ 智能批量处理（按平台自动分组）")
        print("✅ BBDown 集成（字幕优先，音频转录备用）")
        print("✅ 混合链接处理（同时处理多平台链接）")
        return True
    else:
        print("\n❌ 部分功能存在问题")
        return False


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
