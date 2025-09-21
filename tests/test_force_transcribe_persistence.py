#!/usr/bin/env python3
"""
测试强制转录模式配置持久化功能的脚本

用于验证强制转录模式设置能够正确保存到配置文件并在重启后保持。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_persistence():
    """
    测试配置持久化功能
    """
    print("开始测试强制转录模式配置持久化...")
    print("=" * 60)
    
    try:
        from core.config import get_config
        
        # 获取配置实例
        config = get_config()
        
        # 记录原始设置
        original_mode = config.force_transcribe_mode
        print(f"1. 原始强制转录模式设置: {original_mode}")
        
        # 测试设置为True
        print("\n2. 测试设置强制转录模式为True...")
        config.set_force_transcribe_mode(True)
        
        # 验证内存中的设置
        current_mode = config.force_transcribe_mode
        print(f"   内存中的设置: {current_mode}")
        
        if current_mode:
            print("   ✅ 内存设置成功")
        else:
            print("   ❌ 内存设置失败")
            return False
        
        # 重新创建配置实例，模拟程序重启
        print("\n3. 模拟程序重启，重新读取配置...")
        
        # 清除全局配置实例
        import core.config
        core.config._config_instance = None
        
        # 重新获取配置
        new_config = get_config()
        persisted_mode = new_config.force_transcribe_mode
        print(f"   重新读取的设置: {persisted_mode}")
        
        if persisted_mode:
            print("   ✅ 配置持久化成功 (True)")
        else:
            print("   ❌ 配置持久化失败 (True)")
            return False
        
        # 测试设置为False
        print("\n4. 测试设置强制转录模式为False...")
        new_config.set_force_transcribe_mode(False)
        
        # 再次模拟重启
        core.config._config_instance = None
        final_config = get_config()
        final_mode = final_config.force_transcribe_mode
        print(f"   重新读取的设置: {final_mode}")
        
        if not final_mode:
            print("   ✅ 配置持久化成功 (False)")
        else:
            print("   ❌ 配置持久化失败 (False)")
            return False
        
        # 恢复原始设置
        print(f"\n5. 恢复原始设置: {original_mode}")
        final_config.set_force_transcribe_mode(original_mode)
        
        print("\n✅ 强制转录模式配置持久化测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config_file_content():
    """
    测试配置文件内容
    """
    print("\n开始测试配置文件内容...")
    print("=" * 60)
    
    try:
        from core.config import get_config
        
        config = get_config()
        
        # 设置为True并检查文件内容
        print("1. 设置强制转录模式为True...")
        config.set_force_transcribe_mode(True)
        
        # 读取配置文件内容
        with open('config.ini', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'force_transcribe_mode = true' in content:
            print("   ✅ 配置文件中正确写入 'true'")
        else:
            print("   ❌ 配置文件中未找到正确的设置")
            print(f"   配置文件内容:\n{content}")
            return False
        
        # 设置为False并检查文件内容
        print("\n2. 设置强制转录模式为False...")
        config.set_force_transcribe_mode(False)
        
        # 重新读取配置文件内容
        with open('config.ini', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'force_transcribe_mode = false' in content:
            print("   ✅ 配置文件中正确写入 'false'")
        else:
            print("   ❌ 配置文件中未找到正确的设置")
            print(f"   配置文件内容:\n{content}")
            return False
        
        print("\n✅ 配置文件内容测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """
    测试UI集成的配置保存
    """
    print("\n开始测试UI集成的配置保存...")
    print("=" * 60)
    
    try:
        from ui import StreamScribeUI
        from core.config import get_config
        
        # 创建UI实例
        print("1. 创建UI实例...")
        app = StreamScribeUI()
        
        # 记录原始设置
        original_setting = app.force_transcribe_var.get()
        print(f"   UI初始设置: {original_setting}")
        
        # 测试通过UI设置
        print("\n2. 通过UI设置强制转录模式...")
        app.force_transcribe_var.set(True)
        app.on_force_transcribe_changed()
        
        # 检查配置是否保存
        config = get_config()
        saved_setting = config.force_transcribe_mode
        print(f"   配置文件中的设置: {saved_setting}")
        
        if saved_setting:
            print("   ✅ UI设置保存成功")
        else:
            print("   ❌ UI设置保存失败")
            return False
        
        # 恢复原始设置
        app.force_transcribe_var.set(original_setting)
        app.on_force_transcribe_changed()
        
        # 销毁UI
        app.root.destroy()
        
        print("\n✅ UI集成配置保存测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ UI集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("强制转录模式配置持久化测试")
    print("=" * 60)
    
    # 测试配置持久化
    persistence_success = test_config_persistence()
    
    # 测试配置文件内容
    file_content_success = test_config_file_content()
    
    # 测试UI集成
    ui_integration_success = test_ui_integration()
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"- 配置持久化: {'✅ 通过' if persistence_success else '❌ 失败'}")
    print(f"- 配置文件内容: {'✅ 通过' if file_content_success else '❌ 失败'}")
    print(f"- UI集成: {'✅ 通过' if ui_integration_success else '❌ 失败'}")
    
    if persistence_success and file_content_success and ui_integration_success:
        print("\n🎉 所有测试通过！强制转录模式配置持久化功能正常工作。")
        print("\n📋 功能确认:")
        print("- ✅ 设置会正确保存到config.ini文件")
        print("- ✅ 程序重启后设置会保持")
        print("- ✅ UI操作会触发配置保存")
        print("- ✅ 配置文件格式正确")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()
