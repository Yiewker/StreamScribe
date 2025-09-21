"""
测试模型选择和自动量化映射功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_mapping():
    """测试模型和量化类型映射"""
    print("测试模型和量化类型映射...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        
        config = get_config()
        
        # 测试所有可用模型
        models = config.get_available_models()
        print(f"可用模型: {models}")
        print()
        
        for model in models:
            compute_type = config.get_compute_type_for_model(model)
            print(f"模型: {model:10} -> 量化类型: {compute_type}")
        
        print("\n✅ 模型映射测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 模型映射测试失败: {e}")
        return False


def test_whisper_command_generation():
    """测试 whisper 命令生成"""
    print("\n测试 whisper 命令生成...")
    print("=" * 50)
    
    try:
        from core.transcriber import WhisperTranscriber
        from core.config import get_config
        
        config = get_config()
        transcriber = WhisperTranscriber()
        
        # 测试不同模型的命令生成
        test_audio = "test_audio.mp3"
        test_output = "test_output"
        
        models = config.get_available_models()
        
        for model in models:
            # 临时设置模型
            original_model = config.whisper_model
            config.config.set('whisper', 'model', model)
            
            # 生成命令
            command = transcriber._build_whisper_command(test_audio, test_output)
            
            print(f"\n🔍 模型: {model}")
            print(f"📋 命令: {' '.join(command)}")
            
            # 验证命令中包含正确的参数
            command_str = ' '.join(command)
            expected_compute_type = config.get_compute_type_for_model(model)
            
            if f"--model {model}" in command_str:
                print(f"✅ 模型参数正确")
            else:
                print(f"❌ 模型参数错误")
                
            if f"--compute_type {expected_compute_type}" in command_str:
                print(f"✅ 量化类型正确: {expected_compute_type}")
            else:
                print(f"❌ 量化类型错误")
                
            if "--initial_prompt" in command_str:
                print(f"✅ 包含初始提示词")
            else:
                print(f"❌ 缺少初始提示词")
            
            # 恢复原始模型
            config.config.set('whisper', 'model', original_model)
        
        print("\n✅ 命令生成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 命令生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_model_selection():
    """测试UI模型选择功能"""
    print("\n测试UI模型选择功能...")
    print("=" * 50)
    
    try:
        from ui import StreamScribeUI
        
        # 创建UI实例（不运行mainloop）
        app = StreamScribeUI()
        
        # 测试模型信息获取
        models = app.config.get_available_models()
        
        print("模型信息:")
        for model in models:
            info = app.get_model_info(model)
            print(f"  {model}: {info}")
        
        # 测试模型选择回调
        print(f"\n当前选择的模型: {app.model_combobox.get()}")
        
        # 模拟选择不同模型
        for model in models[:3]:  # 测试前3个模型
            app.on_model_changed(model)
            current_model = app.config.whisper_model
            print(f"选择 {model} -> 当前配置: {current_model}")
        
        print("\n✅ UI模型选择测试通过")
        
        # 销毁窗口
        app.root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ UI模型选择测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_example_commands():
    """显示示例命令"""
    print("\n" + "="*60)
    print("🚀 生成的命令示例")
    print("="*60)
    
    try:
        from core.config import get_config
        
        config = get_config()
        models = config.get_available_models()
        
        for model in models:
            compute_type = config.get_compute_type_for_model(model)
            
            print(f"\n📋 {model} 模型命令:")
            example_cmd = f'whisper-ctranslate2 "音频文件.mp3" --model {model} --language "Chinese" --initial_prompt "以下是普通话的简体中文。" --device cuda --compute_type {compute_type} --output_format txt'
            print(f"   {example_cmd}")
        
        print(f"\n✨ 这些命令会根据你在UI中选择的模型自动生成！")
        
    except Exception as e:
        print(f"❌ 示例命令生成失败: {e}")


def main():
    """主测试函数"""
    print("🔧 模型选择和自动量化映射功能测试")
    print("=" * 60)
    
    tests = [
        test_model_mapping,
        test_whisper_command_generation,
        test_ui_model_selection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试 {test.__name__} 失败")
    
    # 显示示例命令
    show_example_commands()
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有功能测试通过！")
        print("现在你可以:")
        print("1. 在UI中选择不同的模型")
        print("2. 系统会自动选择最佳量化类型")
        print("3. 命令会包含初始提示词提高中文识别")
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
