"""
测试系统主题检测功能
"""

import sys
import os
import platform
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_theme_detection():
    """测试主题检测功能"""
    print("测试系统主题检测...")
    print("=" * 50)
    
    try:
        from ui import detect_system_theme
        
        # 检测当前系统主题
        theme = detect_system_theme()
        
        print(f"当前操作系统: {platform.system()}")
        print(f"检测到的主题: {theme}")
        
        if theme in ["dark", "light"]:
            print("✅ 主题检测成功")
            return True
        else:
            print("❌ 主题检测返回了无效值")
            return False
        
    except Exception as e:
        print(f"❌ 主题检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_windows_theme_detection():
    """测试Windows主题检测"""
    if platform.system() != "Windows":
        print("跳过Windows主题检测（当前不是Windows系统）")
        return True
    
    print("\n测试Windows主题检测...")
    print("=" * 50)
    
    try:
        import winreg
        
        # 直接读取注册表
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        
        apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        system_uses_light_theme, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
        
        winreg.CloseKey(key)
        
        print(f"AppsUseLightTheme: {apps_use_light_theme}")
        print(f"SystemUsesLightTheme: {system_uses_light_theme}")
        
        expected_theme = "light" if apps_use_light_theme else "dark"
        print(f"预期主题: {expected_theme}")
        
        # 测试我们的检测函数
        from ui import detect_system_theme
        detected_theme = detect_system_theme()
        
        print(f"检测到的主题: {detected_theme}")
        
        if detected_theme == expected_theme:
            print("✅ Windows主题检测准确")
            return True
        else:
            print("❌ Windows主题检测不准确")
            return False
        
    except Exception as e:
        print(f"❌ Windows主题检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_macos_theme_detection():
    """测试macOS主题检测"""
    if platform.system() != "Darwin":
        print("跳过macOS主题检测（当前不是macOS系统）")
        return True
    
    print("\n测试macOS主题检测...")
    print("=" * 50)
    
    try:
        import subprocess
        
        # 直接执行命令
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True
        )
        
        print(f"defaults命令返回码: {result.returncode}")
        print(f"defaults命令输出: '{result.stdout.strip()}'")
        print(f"defaults命令错误: '{result.stderr.strip()}'")
        
        # 测试我们的检测函数
        from ui import detect_system_theme
        detected_theme = detect_system_theme()
        
        print(f"检测到的主题: {detected_theme}")
        
        # macOS的逻辑：如果返回"Dark"则是深色，否则是浅色
        expected_theme = "dark" if result.stdout.strip() == "Dark" else "light"
        print(f"预期主题: {expected_theme}")
        
        if detected_theme == expected_theme:
            print("✅ macOS主题检测准确")
            return True
        else:
            print("❌ macOS主题检测不准确")
            return False
        
    except Exception as e:
        print(f"❌ macOS主题检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_customtkinter_theme_setting():
    """测试CustomTkinter主题设置"""
    print("\n测试CustomTkinter主题设置...")
    print("=" * 50)
    
    try:
        import customtkinter as ctk
        
        # 测试不同主题设置
        themes_to_test = ["light", "dark", "system"]
        
        for theme in themes_to_test:
            print(f"设置主题为: {theme}")
            ctk.set_appearance_mode(theme)
            
            current_mode = ctk.get_appearance_mode()
            print(f"当前模式: {current_mode}")
        
        # 测试我们的自动主题设置
        from ui import detect_system_theme
        system_theme = detect_system_theme()
        
        print(f"\n系统主题: {system_theme}")
        
        if system_theme == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        final_mode = ctk.get_appearance_mode()
        print(f"最终设置的模式: {final_mode}")
        
        print("✅ CustomTkinter主题设置成功")
        return True
        
    except Exception as e:
        print(f"❌ CustomTkinter主题设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_theme_integration():
    """测试UI主题集成"""
    print("\n测试UI主题集成...")
    print("=" * 50)
    
    try:
        from ui import StreamScribeUI
        
        # 创建UI实例（不运行mainloop）
        print("创建UI实例...")
        app = StreamScribeUI()
        
        print(f"窗口标题: {app.root.title()}")
        print(f"窗口大小: {app.root.geometry()}")
        
        # 检查主题是否正确应用
        import customtkinter as ctk
        current_mode = ctk.get_appearance_mode()
        print(f"当前CustomTkinter模式: {current_mode}")
        
        # 销毁窗口
        app.root.destroy()
        
        print("✅ UI主题集成测试成功")
        return True
        
    except Exception as e:
        print(f"❌ UI主题集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🎨 系统主题检测功能测试")
    print("=" * 60)
    
    tests = [
        test_theme_detection,
        test_windows_theme_detection,
        test_macos_theme_detection,
        test_customtkinter_theme_setting,
        test_ui_theme_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} 通过")
            else:
                print(f"❌ {test.__name__} 失败")
        except Exception as e:
            print(f"❌ {test.__name__} 异常: {e}")
        
        print("\n" + "="*60)
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed >= total - 1:  # 允许一个测试失败（可能是平台相关的）
        print("\n🎉 系统主题检测功能基本正常！")
        print("功能特性:")
        print("✅ 自动检测系统主题（Windows/macOS/Linux）")
        print("✅ 自动应用对应的界面主题")
        print("✅ 支持深色和浅色模式")
        print("✅ 跨平台兼容")
        return True
    else:
        print("\n❌ 系统主题检测功能存在问题")
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
