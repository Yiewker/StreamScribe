#!/usr/bin/env python3
"""
强制转录模式配置持久化演示脚本

演示强制转录模式设置如何保存到配置文件并在程序重启后保持。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_config_persistence():
    """
    演示配置持久化功能
    """
    print("🎯 强制转录模式配置持久化演示")
    print("=" * 60)
    
    from core.config import get_config
    
    # 步骤1：显示当前设置
    print("📋 步骤1：查看当前配置")
    config = get_config()
    current_setting = config.force_transcribe_mode
    print(f"   当前强制转录模式: {current_setting}")
    
    # 步骤2：修改设置
    new_setting = not current_setting
    print(f"\n🔧 步骤2：修改设置为 {new_setting}")
    config.set_force_transcribe_mode(new_setting)
    print(f"   设置已更新为: {config.force_transcribe_mode}")
    
    # 步骤3：显示配置文件内容
    print(f"\n📄 步骤3：查看配置文件内容")
    with open('config.ini', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if 'force_transcribe_mode' in line:
            print(f"   第{i}行: {line.strip()}")
            break
    
    # 步骤4：模拟程序重启
    print(f"\n🔄 步骤4：模拟程序重启")
    print("   清除内存中的配置实例...")
    
    # 清除全局配置实例
    import core.config
    core.config._config_instance = None
    
    # 重新获取配置
    print("   重新加载配置文件...")
    new_config = get_config()
    reloaded_setting = new_config.force_transcribe_mode
    
    print(f"   重新加载后的设置: {reloaded_setting}")
    
    # 步骤5：验证持久化
    print(f"\n✅ 步骤5：验证结果")
    if reloaded_setting == new_setting:
        print("   🎉 配置持久化成功！设置在程序重启后保持不变。")
    else:
        print("   ❌ 配置持久化失败！")
        return False
    
    # 步骤6：恢复原始设置
    print(f"\n🔙 步骤6：恢复原始设置")
    new_config.set_force_transcribe_mode(current_setting)
    print(f"   已恢复为原始设置: {current_setting}")
    
    return True

def demo_ui_integration():
    """
    演示UI集成
    """
    print("\n🎨 UI集成演示")
    print("=" * 60)
    
    try:
        from ui import StreamScribeUI
        from core.config import get_config
        
        print("📋 步骤1：创建UI实例")
        app = StreamScribeUI()
        
        # 获取初始设置
        initial_ui_setting = app.force_transcribe_var.get()
        config = get_config()
        initial_config_setting = config.force_transcribe_mode
        
        print(f"   UI初始设置: {initial_ui_setting}")
        print(f"   配置文件设置: {initial_config_setting}")
        
        if initial_ui_setting == initial_config_setting:
            print("   ✅ UI与配置文件同步正常")
        else:
            print("   ❌ UI与配置文件不同步")
        
        print(f"\n🔧 步骤2：通过UI修改设置")
        new_setting = not initial_ui_setting
        print(f"   设置UI为: {new_setting}")
        
        # 模拟用户点击勾选框
        app.force_transcribe_var.set(new_setting)
        app.on_force_transcribe_changed()
        
        # 检查配置是否保存
        updated_config_setting = config.force_transcribe_mode
        print(f"   配置文件更新为: {updated_config_setting}")
        
        if updated_config_setting == new_setting:
            print("   ✅ UI操作成功保存到配置文件")
        else:
            print("   ❌ UI操作未能保存到配置文件")
            return False
        
        print(f"\n📄 步骤3：查看配置文件变化")
        with open('config.ini', 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_line = f"force_transcribe_mode = {str(new_setting).lower()}"
        if expected_line in content:
            print(f"   ✅ 配置文件包含: {expected_line}")
        else:
            print(f"   ❌ 配置文件未找到预期内容")
            return False
        
        # 恢复原始设置
        print(f"\n🔙 步骤4：恢复原始设置")
        app.force_transcribe_var.set(initial_ui_setting)
        app.on_force_transcribe_changed()
        print(f"   已恢复UI设置为: {initial_ui_setting}")
        
        # 销毁UI
        app.root.destroy()
        
        print("   ✅ UI集成演示完成")
        return True
        
    except Exception as e:
        print(f"   ❌ UI集成演示失败: {str(e)}")
        return False

def show_usage_guide():
    """
    显示使用指南
    """
    print("\n📖 使用指南")
    print("=" * 60)
    
    print("🎯 如何使用强制转录模式配置持久化：")
    print()
    print("1. 🖱️  在StreamScribe界面中勾选/取消勾选'强制转录模式'")
    print("2. 💾  设置会自动保存到config.ini文件")
    print("3. 🔄  关闭并重新打开程序")
    print("4. ✅  设置会自动恢复到上次的状态")
    print()
    print("🔧 配置文件位置：")
    print(f"   {os.path.abspath('config.ini')}")
    print()
    print("📝 配置项说明：")
    print("   [general]")
    print("   force_transcribe_mode = true   # 启用强制转录模式")
    print("   force_transcribe_mode = false  # 禁用强制转录模式")
    print()
    print("💡 提示：")
    print("   - 设置会在勾选/取消勾选时立即保存")
    print("   - 无需手动保存或重启程序")
    print("   - 支持多次切换，每次都会保存")

def main():
    """主函数"""
    print("🚀 强制转录模式配置持久化完整演示")
    print("=" * 60)
    
    try:
        # 演示配置持久化
        config_success = demo_config_persistence()
        
        # 演示UI集成
        ui_success = demo_ui_integration()
        
        # 显示使用指南
        show_usage_guide()
        
        print("\n" + "=" * 60)
        print("📊 演示结果总结：")
        print(f"   配置持久化: {'✅ 成功' if config_success else '❌ 失败'}")
        print(f"   UI集成: {'✅ 成功' if ui_success else '❌ 失败'}")
        
        if config_success and ui_success:
            print("\n🎉 所有功能正常工作！")
            print("   强制转录模式的设置现在会在程序重启后保持。")
            print("   您可以放心使用这个功能了！")
        else:
            print("\n❌ 部分功能存在问题，请检查错误信息。")
            
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
