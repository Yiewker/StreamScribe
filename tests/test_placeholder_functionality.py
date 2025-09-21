#!/usr/bin/env python3
"""
测试URL输入框占位符功能的脚本

用于验证占位符文本的显示、清除和恢复功能是否正常工作。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_placeholder_functionality():
    """
    测试占位符功能
    """
    print("开始测试URL输入框占位符功能...")
    print("=" * 60)
    
    try:
        from ui import StreamScribeUI
        import customtkinter as ctk
        
        # 创建UI实例
        print("1. 创建UI实例...")
        app = StreamScribeUI()
        
        # 检查初始状态
        print("2. 检查初始状态...")
        initial_text = app.url_entry.get("1.0", "end").strip()
        has_placeholder = app.url_entry_has_placeholder
        
        print(f"   初始文本: '{initial_text}'")
        print(f"   占位符状态: {has_placeholder}")
        
        if has_placeholder and initial_text == app.url_placeholder_text:
            print("   ✅ 初始占位符显示正确")
        else:
            print("   ❌ 初始占位符显示错误")
            return False
        
        # 测试获取URL文本（应该返回空字符串）
        print("3. 测试获取URL文本...")
        url_text = app._get_url_text()
        print(f"   获取的URL文本: '{url_text}'")
        
        if url_text == "":
            print("   ✅ 占位符状态下正确返回空字符串")
        else:
            print("   ❌ 占位符状态下应该返回空字符串")
            return False
        
        # 模拟焦点获得（清除占位符）
        print("4. 模拟焦点获得...")
        app._on_url_entry_focus_in(None)
        
        after_focus_text = app.url_entry.get("1.0", "end").strip()
        after_focus_placeholder = app.url_entry_has_placeholder
        
        print(f"   焦点后文本: '{after_focus_text}'")
        print(f"   焦点后占位符状态: {after_focus_placeholder}")
        
        if not after_focus_placeholder and after_focus_text == "":
            print("   ✅ 焦点获得后占位符正确清除")
        else:
            print("   ❌ 焦点获得后占位符清除失败")
            return False
        
        # 模拟输入文本
        print("5. 模拟输入文本...")
        test_url = "https://www.youtube.com/watch?v=test123"
        app.url_entry.insert("1.0", test_url)
        
        input_text = app._get_url_text()
        print(f"   输入后的文本: '{input_text}'")
        
        if input_text == test_url:
            print("   ✅ 输入文本获取正确")
        else:
            print("   ❌ 输入文本获取错误")
            return False
        
        # 模拟焦点失去（有内容，不应该显示占位符）
        print("6. 模拟焦点失去（有内容）...")
        app._on_url_entry_focus_out(None)
        
        focus_out_text = app.url_entry.get("1.0", "end").strip()
        focus_out_placeholder = app.url_entry_has_placeholder
        
        print(f"   失去焦点后文本: '{focus_out_text}'")
        print(f"   失去焦点后占位符状态: {focus_out_placeholder}")
        
        if not focus_out_placeholder and test_url in focus_out_text:
            print("   ✅ 有内容时失去焦点不显示占位符")
        else:
            print("   ❌ 有内容时失去焦点处理错误")
            return False
        
        # 清空内容并失去焦点（应该显示占位符）
        print("7. 清空内容并失去焦点...")
        app.url_entry.delete("1.0", "end")
        app._on_url_entry_focus_out(None)
        
        empty_focus_text = app.url_entry.get("1.0", "end").strip()
        empty_focus_placeholder = app.url_entry_has_placeholder
        
        print(f"   清空后失去焦点文本: '{empty_focus_text}'")
        print(f"   清空后失去焦点占位符状态: {empty_focus_placeholder}")
        
        if empty_focus_placeholder and empty_focus_text == app.url_placeholder_text:
            print("   ✅ 无内容时失去焦点正确显示占位符")
        else:
            print("   ❌ 无内容时失去焦点占位符显示错误")
            return False
        
        # 测试清除功能
        print("8. 测试清除功能...")
        app.url_entry.delete("1.0", "end")
        app.url_entry.insert("1.0", "some test content")
        app.url_entry_has_placeholder = False
        
        # 调用清除功能
        app.clear_all()
        
        clear_text = app.url_entry.get("1.0", "end").strip()
        clear_placeholder = app.url_entry_has_placeholder
        
        print(f"   清除后文本: '{clear_text}'")
        print(f"   清除后占位符状态: {clear_placeholder}")
        
        if clear_placeholder and clear_text == app.url_placeholder_text:
            print("   ✅ 清除功能正确恢复占位符")
        else:
            print("   ❌ 清除功能占位符恢复错误")
            return False
        
        # 销毁UI
        app.root.destroy()
        
        print("\n✅ 所有占位符功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_start_processing_with_placeholder():
    """
    测试在占位符状态下开始处理的行为
    """
    print("\n开始测试占位符状态下的处理行为...")
    print("=" * 60)
    
    try:
        from ui import StreamScribeUI
        from unittest.mock import patch
        
        # 创建UI实例
        app = StreamScribeUI()
        
        # 确保处于占位符状态
        app._set_url_placeholder()
        
        print("1. 确认占位符状态...")
        print(f"   占位符状态: {app.url_entry_has_placeholder}")
        print(f"   获取的URL文本: '{app._get_url_text()}'")
        
        # 模拟点击开始处理按钮
        print("2. 模拟在占位符状态下点击开始处理...")
        
        # 使用patch来模拟messagebox，避免实际弹窗
        with patch('ui.messagebox.showwarning') as mock_warning:
            app.start_processing()
            
            # 检查是否显示了警告
            if mock_warning.called:
                warning_args = mock_warning.call_args[0]
                print(f"   显示警告: {warning_args[1]}")
                print("   ✅ 占位符状态下正确显示警告")
            else:
                print("   ❌ 占位符状态下未显示警告")
                return False
        
        # 销毁UI
        app.root.destroy()
        
        print("\n✅ 占位符状态下处理行为测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("URL输入框占位符功能测试")
    print("=" * 60)
    
    # 测试占位符基本功能
    basic_success = test_placeholder_functionality()
    
    # 测试处理行为
    processing_success = test_start_processing_with_placeholder()
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"- 占位符基本功能: {'✅ 通过' if basic_success else '❌ 失败'}")
    print(f"- 处理行为测试: {'✅ 通过' if processing_success else '❌ 失败'}")
    
    if basic_success and processing_success:
        print("\n🎉 所有测试通过！占位符功能正常工作。")
        print("\n📋 功能确认:")
        print("- ✅ 初始显示占位符文本（灰色）")
        print("- ✅ 获得焦点时自动清除占位符")
        print("- ✅ 输入时占位符不干扰")
        print("- ✅ 失去焦点且无内容时恢复占位符")
        print("- ✅ 清除功能正确恢复占位符")
        print("- ✅ 占位符状态下不会误判为有效输入")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()
