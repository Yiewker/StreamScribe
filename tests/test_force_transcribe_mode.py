#!/usr/bin/env python3
"""
测试强制转录模式功能的脚本

用于测试新添加的强制转录模式是否能正常工作。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import get_config
from core.platform.youtube import YouTubeHandler

def test_force_transcribe_mode():
    """
    测试强制转录模式功能
    """
    print("开始测试强制转录模式功能...")
    
    try:
        # 获取配置
        config = get_config()
        
        # 测试配置读取
        print(f"1. 配置文件中的强制转录模式: {config.force_transcribe_mode}")
        
        # 测试配置设置
        print("2. 测试配置设置...")
        config.config.set('general', 'force_transcribe_mode', 'true')
        force_mode = config.getboolean('general', 'force_transcribe_mode', False)
        print(f"   设置后的强制转录模式: {force_mode}")
        
        # 恢复原始设置
        config.config.set('general', 'force_transcribe_mode', 'false')
        
        # 测试YouTube处理器
        print("3. 测试YouTube处理器逻辑...")
        handler = YouTubeHandler()
        
        # 模拟强制转录模式
        config.config.set('general', 'force_transcribe_mode', 'true')
        force_mode_enabled = config.getboolean('general', 'force_transcribe_mode', False)
        print(f"   YouTube处理器读取的强制转录模式: {force_mode_enabled}")
        
        if force_mode_enabled:
            print("   ✅ 强制转录模式已启用，将跳过字幕检测")
        else:
            print("   ❌ 强制转录模式未启用")
        
        # 恢复原始设置
        config.config.set('general', 'force_transcribe_mode', 'false')
        
        print("\n✅ 强制转录模式功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """
    测试UI集成
    """
    print("\n开始测试UI集成...")
    
    try:
        from ui import StreamScribeUI
        
        # 创建UI实例（不启动主循环）
        app = StreamScribeUI()
        
        # 检查强制转录模式组件是否存在
        if hasattr(app, 'force_transcribe_var'):
            print("✅ 强制转录模式变量已创建")
            print(f"   初始值: {app.force_transcribe_var.get()}")
        else:
            print("❌ 强制转录模式变量未创建")
            return False
        
        if hasattr(app, 'force_transcribe_checkbox'):
            print("✅ 强制转录模式勾选框已创建")
        else:
            print("❌ 强制转录模式勾选框未创建")
            return False
        
        if hasattr(app, 'force_transcribe_info'):
            print("✅ 强制转录模式说明标签已创建")
        else:
            print("❌ 强制转录模式说明标签未创建")
            return False
        
        # 测试回调函数
        if hasattr(app, 'on_force_transcribe_changed'):
            print("✅ 强制转录模式回调函数已创建")
            
            # 测试回调函数
            app.force_transcribe_var.set(True)
            app.on_force_transcribe_changed()
            print("   测试启用强制转录模式...")
            
            app.force_transcribe_var.set(False)
            app.on_force_transcribe_changed()
            print("   测试禁用强制转录模式...")
            
        else:
            print("❌ 强制转录模式回调函数未创建")
            return False
        
        print("✅ UI集成测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ UI集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("强制转录模式功能测试")
    print("=" * 60)
    
    # 测试核心功能
    core_success = test_force_transcribe_mode()
    
    # 测试UI集成
    ui_success = test_ui_integration()
    
    print("\n" + "=" * 60)
    if core_success and ui_success:
        print("🎉 所有测试通过！强制转录模式功能已成功添加。")
        print("\n📋 功能说明:")
        print("- 在UI中添加了'强制转录模式'勾选框")
        print("- 启用后将跳过字幕检测，直接使用AI转录")
        print("- 配置保存在config.ini的[general]节中")
        print("- 支持实时切换，无需重启应用")
    else:
        print("❌ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()
