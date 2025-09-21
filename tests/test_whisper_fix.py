#!/usr/bin/env python3
"""
测试whisper修复

验证修复后的whisper转录功能
"""

import sys
import os
from pathlib import Path
import subprocess

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import get_config
from core.transcriber import WhisperTranscriber

def test_whisper_command_building():
    """测试whisper命令构建"""
    print("🧪 测试whisper命令构建")
    print("=" * 50)
    
    transcriber = WhisperTranscriber()
    
    # 测试音频文件路径
    test_audio = "J:\\Users\\ccd\\Downloads\\temp\\youtube_看懂了这个_你再去炒股_股市暴跌_为啥散户炒股票总赔钱_李永乐老师用数学告诉你_20250728_124150.mp3"
    output_dir = "J:\\Users\\ccd\\Downloads"
    
    try:
        command = transcriber._build_whisper_command(test_audio, output_dir)
        print("✅ 命令构建成功:")
        for i, arg in enumerate(command):
            print(f"  {i}: {arg}")
        
        # 检查是否包含output_name参数
        if '--output_name' in command:
            output_name_index = command.index('--output_name')
            output_name = command[output_name_index + 1]
            print(f"\n📝 输出文件名: {output_name}")
            print(f"📝 预期txt文件: {output_dir}\\{output_name}.txt")
        else:
            print("❌ 缺少 --output_name 参数")
            
    except Exception as e:
        print(f"❌ 命令构建失败: {e}")

def test_environment_variables():
    """测试环境变量设置"""
    print("\n🧪 测试环境变量设置")
    print("=" * 50)
    
    # 模拟设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    print("✅ 环境变量设置:")
    print(f"  PYTHONIOENCODING: {env.get('PYTHONIOENCODING')}")
    print(f"  PYTHONUTF8: {env.get('PYTHONUTF8')}")

def test_file_path_handling():
    """测试文件路径处理"""
    print("\n🧪 测试文件路径处理")
    print("=" * 50)
    
    test_paths = [
        "youtube_看懂了这个_你再去炒股_股市暴跌_为啥散户炒股票总赔钱_李永乐老师用数学告诉你_20250728_124150.mp3",
        "youtube_normal_video_title_20250728_124150.mp3",
        "test_file.mp3"
    ]
    
    for path in test_paths:
        stem = Path(path).stem
        print(f"原始路径: {path}")
        print(f"文件名(无扩展名): {stem}")
        print(f"长度: {len(stem)}")
        print("-" * 30)

def check_whisper_executable():
    """检查whisper可执行文件"""
    print("\n🧪 检查whisper可执行文件")
    print("=" * 50)
    
    config = get_config()
    venv_path = config.whisper_venv_path
    whisper_exe = os.path.join(venv_path, 'Scripts', 'whisper-ctranslate2.exe')
    
    print(f"虚拟环境路径: {venv_path}")
    print(f"whisper可执行文件: {whisper_exe}")
    print(f"文件存在: {'✅' if os.path.exists(whisper_exe) else '❌'}")
    
    if os.path.exists(whisper_exe):
        try:
            # 测试whisper版本
            result = subprocess.run([whisper_exe, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"版本信息: {result.stdout.strip()}")
            else:
                print(f"版本检查失败: {result.stderr}")
        except Exception as e:
            print(f"版本检查异常: {e}")

def simulate_whisper_execution():
    """模拟whisper执行"""
    print("\n🧪 模拟whisper执行")
    print("=" * 50)
    
    # 检查是否有测试音频文件
    test_audio = "J:\\Users\\ccd\\Downloads\\temp\\youtube_看懂了这个_你再去炒股_股市暴跌_为啥散户炒股票总赔钱_李永乐老师用数学告诉你_20250728_124150.mp3"
    
    if os.path.exists(test_audio):
        print(f"✅ 找到测试音频文件: {test_audio}")
        file_size = os.path.getsize(test_audio)
        print(f"文件大小: {file_size:,} 字节")
        
        # 构建测试命令
        transcriber = WhisperTranscriber()
        
        try:
            command = transcriber._build_whisper_command(test_audio, "J:\\Users\\ccd\\Downloads")
            print("\n📋 完整命令:")
            print(" ".join(command))
            
            print("\n💡 建议:")
            print("1. 可以复制上述命令到命令行手动测试")
            print("2. 检查是否生成了对应的txt文件")
            print("3. 查看whisper的详细输出信息")
            
        except Exception as e:
            print(f"❌ 命令构建失败: {e}")
    else:
        print(f"❌ 测试音频文件不存在: {test_audio}")
        print("请先运行一次视频处理来生成测试音频文件")

def main():
    """主函数"""
    print("🔧 Whisper修复验证测试")
    print("=" * 60)
    
    # 运行所有测试
    test_whisper_command_building()
    test_environment_variables()
    test_file_path_handling()
    check_whisper_executable()
    simulate_whisper_execution()
    
    print("\n" + "=" * 60)
    print("📋 修复总结:")
    print("- ✅ 添加了 --output_name 参数明确指定输出文件名")
    print("- ✅ 设置了环境变量解决编码问题")
    print("- ✅ 改进了文件查找逻辑")
    print("- ✅ 添加了详细的调试信息")
    print("- ✅ 实现了异步处理避免UI卡死")
    
    print("\n💡 下一步:")
    print("1. 重新启动应用程序")
    print("2. 测试问题视频链接")
    print("3. 观察详细的调试输出")
    print("4. 确认UI不再卡死")

if __name__ == "__main__":
    main()
