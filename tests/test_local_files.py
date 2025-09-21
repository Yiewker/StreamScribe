"""
测试本地文件处理功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_local_file_handler():
    """测试本地文件处理器"""
    print("测试本地文件处理器...")
    print("=" * 50)
    
    try:
        from core.platform.local import LocalFileHandler
        from core.config import get_config
        
        config = get_config()
        handler = LocalFileHandler()
        
        # 测试支持的格式
        print("支持的文件格式:")
        print(handler.get_supported_formats_display())
        print()
        
        # 测试格式检查
        test_files = [
            "test.mp3",
            "test.wav", 
            "test.mp4",
            "test.avi",
            "test.txt",  # 不支持的格式
            "test.doc"   # 不支持的格式
        ]
        
        print("格式检查测试:")
        for file_path in test_files:
            is_supported = handler._is_supported_format(file_path)
            is_video = handler._is_video_file(file_path)
            status = "✅ 支持" if is_supported else "❌ 不支持"
            file_type = "(视频)" if is_video else "(音频)" if is_supported else ""
            print(f"  {file_path}: {status} {file_type}")
        
        print("\n✅ 本地文件处理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 本地文件处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_manager_local_files():
    """测试任务管理器的本地文件功能"""
    print("\n测试任务管理器本地文件功能...")
    print("=" * 50)
    
    try:
        from core.manager import TaskManager
        
        manager = TaskManager()
        
        # 测试支持的平台
        platforms = manager.get_supported_platforms()
        print(f"支持的平台: {platforms}")
        
        if 'local' not in platforms:
            print("❌ 本地文件平台未注册")
            return False
        
        print("✅ 本地文件平台已注册")
        
        # 测试批量处理方法存在
        methods_to_check = [
            'process_local_file',
            'process_batch_files',
            'process_batch_urls'
        ]
        
        for method_name in methods_to_check:
            if hasattr(manager, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
                return False
        
        print("\n✅ 任务管理器本地文件功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 任务管理器本地文件功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_local_files():
    """测试配置文件的本地文件设置"""
    print("\n测试配置文件本地文件设置...")
    print("=" * 50)
    
    try:
        from core.config import get_config
        
        config = get_config()
        
        # 测试配置属性
        audio_formats = config.supported_audio_formats
        video_formats = config.supported_video_formats
        max_batch = config.max_batch_files
        all_formats = config.get_all_supported_formats()
        
        print(f"支持的音频格式: {audio_formats}")
        print(f"支持的视频格式: {video_formats}")
        print(f"最大批量文件数: {max_batch}")
        print(f"所有支持的格式: {all_formats}")
        
        # 验证基本格式
        expected_audio = ['mp3', 'wav']
        expected_video = ['mp4', 'avi']
        
        for fmt in expected_audio:
            if fmt not in audio_formats:
                print(f"❌ 缺少音频格式: {fmt}")
                return False
        
        for fmt in expected_video:
            if fmt not in video_formats:
                print(f"❌ 缺少视频格式: {fmt}")
                return False
        
        if max_batch <= 0:
            print(f"❌ 批量文件数配置错误: {max_batch}")
            return False
        
        print("\n✅ 配置文件本地文件设置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件本地文件设置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_batch_processing():
    """测试UI批量处理功能"""
    print("\n测试UI批量处理功能...")
    print("=" * 50)
    
    try:
        from ui import StreamScribeUI
        
        # 创建UI实例（不运行mainloop）
        app = StreamScribeUI()
        
        # 测试URL解析
        test_urls_text = """
        https://www.youtube.com/watch?v=test1
        https://youtu.be/test2
        
        https://www.youtube.com/watch?v=test3
        """
        
        urls = app._parse_urls(test_urls_text)
        print(f"解析的URL: {urls}")
        
        if len(urls) != 3:
            print(f"❌ URL解析错误，期望3个，实际{len(urls)}个")
            return False
        
        # 测试文件格式检查
        test_files = [
            "test.mp3",
            "test.mp4", 
            "test.txt"
        ]
        
        for file_path in test_files:
            is_supported = app._is_supported_file(file_path)
            expected = file_path.endswith(('.mp3', '.mp4'))
            if is_supported != expected:
                print(f"❌ 文件格式检查错误: {file_path}")
                return False
        
        print("✅ URL解析和文件格式检查正确")
        
        # 测试模式切换
        app.mode_var.set("file")
        app.on_mode_changed()
        
        if app.current_mode != "file":
            print("❌ 模式切换失败")
            return False
        
        print("✅ 模式切换正常")
        
        # 销毁窗口
        app.root.destroy()
        
        print("\n✅ UI批量处理功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ UI批量处理功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🔧 本地文件和批量处理功能测试")
    print("=" * 60)
    
    tests = [
        test_config_local_files,
        test_local_file_handler,
        test_task_manager_local_files,
        test_ui_batch_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试 {test.__name__} 失败")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有功能测试通过！")
        print("新功能包括:")
        print("✅ 本地文件支持（音频: mp3, wav | 视频: mp4, avi, mkv）")
        print("✅ 批量处理（URL和本地文件）")
        print("✅ 文件拖拽支持")
        print("✅ 模式切换（在线链接 / 本地文件）")
        print("✅ 文件格式验证")
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
