#!/usr/bin/env python3
"""
实际测试whisper输出

手动运行whisper命令来看看实际生成了什么文件
"""

import sys
import os
from pathlib import Path
import subprocess
import time

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import get_config

def test_whisper_manually():
    """手动测试whisper命令"""
    print("🧪 手动测试whisper命令")
    print("=" * 60)
    
    # 检查音频文件
    audio_file = "J:\\Users\\ccd\\Downloads\\temp\\youtube_看懂了这个_你再去炒股_股市暴跌_为啥散户炒股票总赔钱_李永乐老师用数学告诉你_20250728_125308.mp3"
    output_dir = "J:\\Users\\ccd\\Downloads"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return
    
    print(f"✅ 音频文件存在: {audio_file}")
    print(f"文件大小: {os.path.getsize(audio_file):,} 字节")
    
    # 构建简化的whisper命令
    config = get_config()
    venv_path = config.whisper_venv_path
    whisper_exe = os.path.join(venv_path, 'Scripts', 'whisper-ctranslate2.exe')
    
    # 简化命令，只保留必要参数
    command = [
        whisper_exe,
        audio_file,
        '--model', 'base',  # 使用更快的模型进行测试
        '--output_format', 'txt',
        '--output_dir', output_dir,
        '--device', 'cpu',  # 使用CPU避免GPU问题
        '--verbose', 'True'  # 启用详细输出
    ]
    
    print(f"\n📋 测试命令:")
    print(" ".join(command))
    
    # 记录执行前的文件列表
    print(f"\n📁 执行前输出目录文件:")
    before_files = set()
    try:
        for file in Path(output_dir).iterdir():
            if file.is_file() and file.suffix.lower() in ['.txt', '.srt', '.vtt']:
                before_files.add(file.name)
                print(f"  - {file.name}")
    except Exception as e:
        print(f"无法列出文件: {e}")
    
    # 执行命令
    print(f"\n🚀 执行whisper命令...")
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        
        start_time = time.time()
        result = subprocess.run(
            command,
            capture_output=True,
            env=env,
            timeout=300  # 5分钟超时
        )
        end_time = time.time()
        
        print(f"⏱️ 执行时间: {end_time - start_time:.1f} 秒")
        print(f"📊 返回码: {result.returncode}")
        
        # 解码输出
        try:
            stdout = result.stdout.decode('utf-8', errors='ignore')
            stderr = result.stderr.decode('utf-8', errors='ignore')
        except:
            stdout = str(result.stdout)
            stderr = str(result.stderr)
        
        if stdout.strip():
            print(f"\n📤 标准输出:")
            print(stdout[:1000] + "..." if len(stdout) > 1000 else stdout)
        
        if stderr.strip():
            print(f"\n📤 错误输出:")
            print(stderr[:1000] + "..." if len(stderr) > 1000 else stderr)
        
        # 检查执行后的文件
        print(f"\n📁 执行后输出目录新文件:")
        after_files = set()
        new_files = []
        try:
            for file in Path(output_dir).iterdir():
                if file.is_file() and file.suffix.lower() in ['.txt', '.srt', '.vtt']:
                    after_files.add(file.name)
                    if file.name not in before_files:
                        new_files.append(file)
                        print(f"  🆕 {file.name}")
        except Exception as e:
            print(f"无法列出文件: {e}")
        
        if new_files:
            print(f"\n🎉 找到 {len(new_files)} 个新生成的文件!")
            for file in new_files:
                print(f"\n📄 文件: {file.name}")
                print(f"   大小: {file.stat().st_size} 字节")
                print(f"   修改时间: {time.ctime(file.stat().st_mtime)}")
                
                # 显示文件内容预览
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read(200)
                        print(f"   内容预览: {content}...")
                except Exception as e:
                    print(f"   无法读取内容: {e}")
        else:
            print("❌ 没有找到新生成的文件")
            
    except subprocess.TimeoutExpired:
        print("❌ 命令执行超时")
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")

def check_whisper_version():
    """检查whisper版本和支持的参数"""
    print("\n🔍 检查whisper版本和参数")
    print("=" * 60)
    
    config = get_config()
    venv_path = config.whisper_venv_path
    whisper_exe = os.path.join(venv_path, 'Scripts', 'whisper-ctranslate2.exe')
    
    try:
        # 检查版本
        result = subprocess.run([whisper_exe, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 版本: {result.stdout.strip()}")
        
        # 检查帮助信息（查看支持的参数）
        result = subprocess.run([whisper_exe, '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            help_text = result.stdout
            # 检查是否支持output_name参数
            if '--output_name' in help_text:
                print("✅ 支持 --output_name 参数")
            else:
                print("❌ 不支持 --output_name 参数")
                
            # 查找输出相关的参数
            print("\n📋 输出相关参数:")
            lines = help_text.split('\n')
            for line in lines:
                if 'output' in line.lower():
                    print(f"  {line.strip()}")
                    
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def main():
    """主函数"""
    print("🔧 Whisper实际输出调试")
    print("=" * 60)
    
    # 检查版本和参数支持
    check_whisper_version()
    
    # 手动测试whisper
    test_whisper_manually()
    
    print("\n💡 调试建议:")
    print("1. 如果whisper成功生成了文件，检查文件名是否与预期匹配")
    print("2. 如果没有生成文件，检查whisper的错误输出")
    print("3. 考虑使用更简单的文件名进行测试")
    print("4. 检查输出目录的权限")

if __name__ == "__main__":
    main()
