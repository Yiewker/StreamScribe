"""
测试优化后的 whisper-ctranslate2 性能
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_optimized_transcription():
    """测试优化后的转录性能"""
    print("测试优化后的 whisper-ctranslate2 性能...")
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试无字幕的视频
        test_url = "https://www.youtube.com/watch?v=lPVVPQ5vwQo"
        
        print(f"测试 URL: {test_url}")
        print("开始性能测试...")
        print("优化选项:")
        print("  - 批处理推理: 启用 (batch_size=16)")
        print("  - 量化类型: int8")
        print("  - VAD 语音活动检测: 启用")
        print("  - 设备: CPU")
        print()
        
        start_time = time.time()
        
        def status_callback(message):
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] {message}")
        
        result = manager.process_url(test_url, status_callback)
        
        total_time = time.time() - start_time
        
        if result['success']:
            print(f"\n✓ 优化后转录成功!")
            print(f"  总耗时: {total_time:.1f} 秒")
            print(f"  处理方式: {result.get('method', 'unknown')}")
            print(f"  文稿文件: {result['transcript_file']}")
            
            # 读取并显示转录结果
            if Path(result['transcript_file']).exists():
                with open(result['transcript_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"\n转录内容预览:")
                    print("-" * 50)
                    print(content[:400] + "..." if len(content) > 400 else content)
                    print("-" * 50)
            
            return True
        else:
            print(f"\n✗ 转录失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_optimization_tips():
    """显示进一步的优化建议"""
    print("\n" + "="*60)
    print("🚀 进一步优化建议:")
    print("="*60)
    
    print("\n1. 🖥️ GPU 加速 (如果有 NVIDIA GPU):")
    print("   在 config.ini 中修改:")
    print("   device = cuda")
    print("   compute_type = float16")
    print("   预期速度提升: 5-10x")
    
    print("\n2. 📦 模型选择优化:")
    print("   - tiny: 最快，准确度较低")
    print("   - base: 平衡")
    print("   - small: 当前使用，推荐")
    print("   - medium: 更准确，但慢 2-3x")
    print("   - large: 最准确，但慢 4-5x")
    
    print("\n3. ⚡ 批处理大小调整:")
    print("   - 增加 batch_size (16 -> 32) 可能更快")
    print("   - 但会消耗更多内存")
    
    print("\n4. 🎯 VAD 参数微调:")
    print("   可在命令中添加:")
    print("   --vad_onset 0.5")
    print("   --vad_min_speech_duration_ms 250")
    
    print("\n5. 🔧 量化类型选择:")
    print("   CPU: int8 (当前) > int16 > float32")
    print("   GPU: float16 > int8 > float32")


def main():
    """主测试函数"""
    print("whisper-ctranslate2 性能优化测试")
    print("=" * 50)
    
    # 询问是否进行测试
    print("这将测试优化后的 AI 转录性能")
    print("测试可能需要几分钟时间")
    choice = input("是否开始测试？(y/n): ").strip().lower()
    
    if choice != 'y':
        print("跳过性能测试")
        show_optimization_tips()
        return True
    
    # 执行性能测试
    success = test_optimized_transcription()
    
    # 显示优化建议
    show_optimization_tips()
    
    return success


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
