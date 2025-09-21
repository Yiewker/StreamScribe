"""
StreamScribe 核心功能测试脚本

用于测试各个模块的基本功能。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """测试配置模块"""
    print("测试配置模块...")
    try:
        from core.config import get_config
        config = get_config()
        
        print(f"  yt-dlp 路径: {config.yt_dlp_path}")
        print(f"  Whisper 虚拟环境: {config.whisper_venv_path}")
        print(f"  输出目录: {config.output_dir}")
        print(f"  临时目录: {config.temp_dir}")
        print(f"  代理设置: {config.proxy}")
        print("  配置模块测试通过 ✓")
        return True
    except Exception as e:
        print(f"  配置模块测试失败: {e}")
        return False

def test_utils():
    """测试工具函数模块"""
    print("\n测试工具函数模块...")
    try:
        from core.utils import (
            extract_video_id_from_url, 
            validate_url, 
            sanitize_filename,
            generate_output_filename
        )
        
        # 测试 URL 验证
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "invalid_url"
        ]
        
        for url in test_urls:
            is_valid = validate_url(url)
            platform, video_id = extract_video_id_from_url(url)
            print(f"  URL: {url}")
            print(f"    有效: {is_valid}, 平台: {platform}, ID: {video_id}")
        
        # 测试文件名清理
        test_filename = "Test Video: <Special> Characters/\\|?*"
        clean_filename = sanitize_filename(test_filename)
        print(f"  文件名清理: '{test_filename}' -> '{clean_filename}'")
        
        # 测试输出文件名生成
        output_filename = generate_output_filename("Test Video", "youtube")
        print(f"  生成文件名: {output_filename}")
        
        print("  工具函数模块测试通过 ✓")
        return True
    except Exception as e:
        print(f"  工具函数模块测试失败: {e}")
        return False

def test_manager():
    """测试任务管理器"""
    print("\n测试任务管理器...")
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试支持的平台
        platforms = manager.get_supported_platforms()
        print(f"  支持的平台: {platforms}")
        
        # 测试平台信息获取
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        platform_info = manager.get_platform_info(test_url)
        print(f"  平台信息: {platform_info}")
        
        print("  任务管理器测试通过 ✓")
        return True
    except Exception as e:
        print(f"  任务管理器测试失败: {e}")
        return False

def test_youtube_handler():
    """测试 YouTube 处理器"""
    print("\n测试 YouTube 处理器...")
    try:
        from core.platform.youtube import YouTubeHandler
        
        handler = YouTubeHandler()
        print("  YouTube 处理器初始化成功")
        
        # 注意：这里不进行实际的网络请求测试，只测试初始化
        print("  YouTube 处理器测试通过 ✓")
        return True
    except Exception as e:
        print(f"  YouTube 处理器测试失败: {e}")
        return False

def test_transcriber():
    """测试转录器"""
    print("\n测试转录器...")
    try:
        from core.transcriber import WhisperTranscriber
        
        transcriber = WhisperTranscriber()
        
        # 测试支持的格式
        formats = transcriber.get_supported_formats()
        print(f"  支持的音频格式: {formats}")
        
        print("  转录器测试通过 ✓")
        return True
    except Exception as e:
        print(f"  转录器测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n测试依赖项...")
    try:
        from core.config import get_config
        config = get_config()
        
        # 检查 yt-dlp
        yt_dlp_exists = os.path.exists(config.yt_dlp_path)
        print(f"  yt-dlp 存在: {yt_dlp_exists}")
        
        # 检查 Whisper 虚拟环境
        whisper_python = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        whisper_exists = os.path.exists(whisper_python)
        print(f"  Whisper 虚拟环境存在: {whisper_exists}")
        
        # 检查目录
        output_dir_exists = os.path.exists(config.output_dir)
        print(f"  输出目录存在: {output_dir_exists}")
        
        if yt_dlp_exists and whisper_exists and output_dir_exists:
            print("  依赖项测试通过 ✓")
            return True
        else:
            print("  依赖项测试失败 ✗")
            return False
            
    except Exception as e:
        print(f"  依赖项测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("StreamScribe 核心功能测试")
    print("=" * 50)
    
    tests = [
        test_config,
        test_utils,
        test_manager,
        test_youtube_handler,
        test_transcriber,
        test_dependencies
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
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
