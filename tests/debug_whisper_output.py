#!/usr/bin/env python3
"""
调试whisper输出文件

检查whisper-ctranslate2实际生成了什么文件
"""

import sys
import os
from pathlib import Path
import time

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import get_config

def check_recent_files():
    """检查最近生成的文件"""
    config = get_config()
    output_dir = Path(config.output_dir)
    
    print(f"🔍 检查输出目录: {output_dir}")
    print("=" * 60)
    
    if not output_dir.exists():
        print("❌ 输出目录不存在")
        return
    
    # 获取最近5分钟内的文件
    current_time = time.time()
    recent_files = []
    
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            mtime = file_path.stat().st_mtime
            age_minutes = (current_time - mtime) / 60
            
            if age_minutes < 5:  # 5分钟内
                recent_files.append((file_path, mtime, age_minutes))
    
    if not recent_files:
        print("📝 最近5分钟内没有新文件")
        return
    
    # 按修改时间排序
    recent_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📋 最近5分钟内的文件 ({len(recent_files)} 个):")
    for file_path, mtime, age_minutes in recent_files:
        size = file_path.stat().st_size
        print(f"  📄 {file_path.name}")
        print(f"     大小: {size:,} 字节")
        print(f"     修改时间: {time.ctime(mtime)}")
        print(f"     距离现在: {age_minutes:.1f} 分钟")
        
        # 如果是文本文件，显示前几行内容
        if file_path.suffix.lower() in ['.txt', '.srt', '.vtt']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(200)  # 读取前200字符
                    print(f"     内容预览: {content[:100]}...")
            except Exception as e:
                print(f"     无法读取内容: {e}")
        print()

def check_temp_files():
    """检查临时目录中的文件"""
    config = get_config()
    temp_dir = Path(config.temp_dir)
    
    print(f"🔍 检查临时目录: {temp_dir}")
    print("=" * 60)
    
    if not temp_dir.exists():
        print("❌ 临时目录不存在")
        return
    
    # 查找音频文件
    audio_files = []
    for ext in ['.mp3', '.wav', '.m4a']:
        audio_files.extend(temp_dir.glob(f"*{ext}"))
    
    if audio_files:
        print(f"🎵 找到 {len(audio_files)} 个音频文件:")
        for audio_file in sorted(audio_files, key=lambda f: f.stat().st_mtime, reverse=True):
            size = audio_file.stat().st_size
            mtime = time.ctime(audio_file.stat().st_mtime)
            print(f"  🎵 {audio_file.name}")
            print(f"     大小: {size:,} 字节")
            print(f"     修改时间: {mtime}")
            print()
    else:
        print("📝 没有找到音频文件")

def simulate_whisper_filename(audio_path):
    """模拟whisper可能生成的文件名"""
    audio_name = Path(audio_path).stem
    
    print(f"🧪 模拟whisper文件名生成")
    print("=" * 60)
    print(f"原始音频文件名: {audio_name}")
    print(f"文件名长度: {len(audio_name)}")
    
    # whisper可能的文件名变体
    variants = [
        audio_name,  # 完整文件名
        audio_name[:100],  # 截断到100字符
        audio_name[:80],   # 截断到80字符
        audio_name[:60],   # 截断到60字符
    ]
    
    print("\n可能的whisper输出文件名:")
    for i, variant in enumerate(variants):
        print(f"  {i+1}. {variant}.txt")
        print(f"     长度: {len(variant)}")
    print()

def main():
    """主函数"""
    print("🔧 Whisper输出文件调试工具")
    print("=" * 60)
    
    # 检查最近的文件
    check_recent_files()
    
    # 检查临时文件
    check_temp_files()
    
    # 模拟文件名
    test_audio = "youtube_看懂了这个_你再去炒股_股市暴跌_为啥散户炒股票总赔钱_李永乐老师用数学告诉你_20250728_123233.mp3"
    simulate_whisper_filename(test_audio)
    
    print("💡 建议:")
    print("1. 检查whisper是否真的生成了文件")
    print("2. 确认文件名是否被截断")
    print("3. 检查文件权限和路径问题")
    print("4. 查看whisper的详细错误输出")

if __name__ == "__main__":
    main()
