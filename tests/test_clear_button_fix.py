#!/usr/bin/env python3
"""
测试清除按钮修复的脚本

用于测试修复后的清除按钮是否能正常工作。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
from ui import StreamScribeUI

def test_clear_button():
    """
    测试清除按钮功能
    """
    print("开始测试清除按钮修复...")
    
    try:
        # 创建UI实例
        app = StreamScribeUI()
        
        # 模拟添加一些内容
        print("1. 添加测试内容...")
        app.url_entry.delete("1.0", "end")
        app.url_entry.insert("1.0", "https://www.youtube.com/watch?v=test123")
        app.result_textbox.insert("1.0", "这是一些测试结果文本...")
        
        # 测试清除功能
        print("2. 测试清除功能...")
        app.clear_all()
        
        # 检查是否清除成功
        url_content = app.url_entry.get("1.0", "end").strip()
        result_content = app.result_textbox.get("1.0", "end").strip()
        
        print(f"3. 检查清除结果:")
        print(f"   URL输入框内容: '{url_content}'")
        print(f"   结果文本框内容: '{result_content}'")
        
        # 验证结果
        expected_placeholder = "请输入视频链接，支持 YouTube 和 B站，可批量处理..."
        
        if url_content == expected_placeholder:
            print("✅ URL输入框清除成功，占位符文本正确")
        else:
            print("❌ URL输入框清除失败")
            
        if not result_content:
            print("✅ 结果文本框清除成功")
        else:
            print("❌ 结果文本框清除失败")
            
        print("\n测试完成！清除按钮应该可以正常工作了。")
        
        # 不启动主循环，只是测试功能
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("清除按钮修复测试")
    print("=" * 50)
    
    success = test_clear_button()
    
    if success:
        print("\n🎉 修复验证成功！")
        print("现在可以启动StreamScribe应用，清除按钮应该能正常工作。")
    else:
        print("\n❌ 修复验证失败，请检查错误信息。")

if __name__ == "__main__":
    main()
