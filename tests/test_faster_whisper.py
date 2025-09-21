"""
测试 faster_whisper 的使用方式
"""

import os
import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_faster_whisper_usage():
    """测试 faster_whisper 的使用方式"""
    print("测试 faster_whisper 的使用方式...")
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        # 测试 faster_whisper 的基本功能
        test_code = '''
import faster_whisper
print("faster_whisper 版本:", faster_whisper.__version__)

# 测试模型初始化
try:
    model = faster_whisper.WhisperModel("small", device="cpu")
    print("✓ 模型初始化成功")
    print("模型信息:", type(model))
except Exception as e:
    print("✗ 模型初始化失败:", e)
'''
        
        print("执行 faster_whisper 测试代码...")
        
        result = subprocess.run(
            [python_exe, '-c', test_code],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✓ faster_whisper 基本功能测试成功")
            print(result.stdout)
            return True
        else:
            print("✗ faster_whisper 基本功能测试失败")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def test_faster_whisper_transcribe():
    """测试 faster_whisper 转录功能"""
    print("\n测试 faster_whisper 转录功能...")
    
    test_file = r"J:\Users\ccd\Downloads\temp\test1.mp3"
    
    if not os.path.exists(test_file):
        print(f"✗ 测试文件不存在: {test_file}")
        return False
    
    try:
        from core.config import get_config
        config = get_config()
        
        python_exe = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
        
        # 创建转录测试代码
        test_code = f'''
import faster_whisper
import os

print("开始转录测试...")
audio_file = r"{test_file}"

try:
    # 初始化模型
    model = faster_whisper.WhisperModel("small", device="cpu")
    print("✓ 模型加载成功")
    
    # 转录音频
    segments, info = model.transcribe(audio_file, language="zh")
    print(f"✓ 转录完成，检测语言: {{info.language}}, 概率: {{info.language_probability:.2f}}")
    
    # 收集转录结果
    transcript_text = ""
    for segment in segments:
        transcript_text += segment.text + "\\n"
        print(f"[{{segment.start:.2f}}s -> {{segment.end:.2f}}s] {{segment.text}}")
    
    # 保存结果
    output_file = r"{config.output_dir}\\test_faster_whisper_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    
    print(f"✓ 转录结果已保存到: {{output_file}}")
    print(f"转录文本预览: {{transcript_text[:100]}}...")
    
except Exception as e:
    print(f"✗ 转录失败: {{e}}")
    import traceback
    traceback.print_exc()
'''
        
        print(f"执行转录测试...")
        
        result = subprocess.run(
            [python_exe, '-c', test_code],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print("✓ faster_whisper 转录测试成功")
            print(result.stdout)
            return True
        else:
            print("✗ faster_whisper 转录测试失败")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False


def main():
    """主函数"""
    print("faster_whisper 功能测试")
    print("=" * 40)
    
    tests = [
        test_faster_whisper_usage,
        test_faster_whisper_transcribe
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试 {test.__name__} 失败")
            break
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ faster_whisper 功能正常，可以使用！")
        return True
    else:
        print("✗ faster_whisper 功能存在问题")
        return False


if __name__ == "__main__":
    try:
        success = main()
        input(f"\n{'成功' if success else '失败'}！按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
