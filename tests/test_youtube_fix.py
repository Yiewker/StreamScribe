#!/usr/bin/env python3
"""
测试YouTube处理修复的脚本

用于测试修复后的YouTube处理器是否能正确处理之前失败的视频链接。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.manager import TaskManager
from core.utils import setup_logging

def test_youtube_video(url):
    """
    测试单个YouTube视频的处理
    
    Args:
        url (str): YouTube视频链接
    """
    print(f"\n{'='*60}")
    print(f"测试视频: {url}")
    print(f"{'='*60}")
    
    # 设置日志
    logger = setup_logging()
    
    # 创建任务管理器
    manager = TaskManager()
    
    def status_callback(message):
        print(f"📢 状态: {message}")
    
    try:
        # 处理视频
        result = manager.process_url(url, status_callback)
        
        if result['success']:
            print(f"✅ 处理成功!")
            print(f"   平台: {result.get('platform', 'Unknown')}")
            print(f"   方法: {result.get('method', 'Unknown')}")
            print(f"   视频标题: {result.get('video_title', 'Unknown')}")
            print(f"   文稿文件: {result.get('transcript_file', 'Unknown')}")
        else:
            print(f"❌ 处理失败: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 处理过程中发生异常: {str(e)}")
    
    print(f"{'='*60}\n")

def main():
    """主函数"""
    print("YouTube处理修复测试")
    print("=" * 60)
    
    # 测试之前失败的视频链接
    test_urls = [
        "https://www.youtube.com/watch?v=0H_UpFLEs8Q",  # 之前失败的链接
        # 可以添加更多测试链接
    ]
    
    for url in test_urls:
        test_youtube_video(url)
    
    print("测试完成!")

if __name__ == "__main__":
    main()
