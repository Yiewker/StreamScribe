#!/usr/bin/env python3
"""
测试新功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import Config

def test_tools_path_reading():
    """测试从tools_path.txt读取工具路径"""
    print("=" * 60)
    print("测试1: 从tools_path.txt读取工具路径")
    print("=" * 60)
    
    config = Config()
    
    print(f"\n✅ whisper-ctranslate2路径: {config._tools_paths.get('whisper_exe', 'N/A')}")
    print(f"✅ yt-dlp路径: {config.yt_dlp_path}")
    print(f"✅ BBDown路径: {config.bbdown_path}")
    print(f"✅ Whisper虚拟环境路径: {config.whisper_venv_path}")
    
def test_new_models():
    """测试新模型支持"""
    print("\n" + "=" * 60)
    print("测试2: 新模型支持")
    print("=" * 60)
    
    config = Config()
    
    models = config.get_available_models()
    print(f"\n✅ 可用模型列表: {models}")
    
    # 测试新模型的量化类型
    print("\n新模型的量化类型:")
    print(f"  - large-v3-turbo: {config.get_compute_type_for_model('large-v3-turbo')}")
    print(f"  - belle-whisper-v3-zh-punct: {config.get_compute_type_for_model('belle-whisper-v3-zh-punct')}")
    
    # 测试belle模型的目录
    belle_dir = config.get_model_directory('belle-whisper-v3-zh-punct')
    print(f"\n✅ belle模型目录: {belle_dir}")
    
def test_srt_format():
    """测试SRT格式配置"""
    print("\n" + "=" * 60)
    print("测试3: SRT格式配置")
    print("=" * 60)
    
    config = Config()
    
    print(f"\n✅ 当前SRT格式设置: {config.whisper_output_format_srt}")
    
    # 测试设置SRT格式
    print("\n测试设置SRT格式为False...")
    config.set_output_format_srt(False)
    print(f"✅ 设置后的值: {config.whisper_output_format_srt}")
    
    # 恢复为True
    print("\n恢复SRT格式为True...")
    config.set_output_format_srt(True)
    print(f"✅ 恢复后的值: {config.whisper_output_format_srt}")

def test_batch_removed():
    """测试batch参数已移除"""
    print("\n" + "=" * 60)
    print("测试4: 确认batch参数已移除")
    print("=" * 60)

    config = Config()

    # 检查Config类的源代码中是否还有batch相关方法
    import inspect
    source = inspect.getsource(Config)

    has_batched_in_source = 'whisper_batched' in source
    has_batch_size_in_source = 'whisper_batch_size' in source

    if not has_batched_in_source and not has_batch_size_in_source:
        print("\n✅ batch相关参数已成功从Config类中移除")
    else:
        print("\n❌ 警告: batch相关参数仍在源代码中")
        if has_batched_in_source:
            print("  - 发现 whisper_batched")
        if has_batch_size_in_source:
            print("  - 发现 whisper_batch_size")

def main():
    """主测试函数"""
    print("\n🔍 StreamScribe 新功能测试")
    print("=" * 60)
    
    try:
        test_tools_path_reading()
        test_new_models()
        test_srt_format()
        test_batch_removed()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

