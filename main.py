"""
StreamScribe 主程序入口

GUI主程序入口，负责UI的创建和事件绑定。
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
try:
    from ui_compact import StreamScribeCompactUI
    from core.utils import setup_logging, clean_temp_files
    from core.config import get_config
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包: pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """检查基本依赖项是否满足（绿色版模式：只检查必要项）"""
    config = get_config()

    # 对于绿色版，我们只检查目录创建权限，不检查外部工具路径
    # 外部工具路径将在实际使用时进行检查和提示

    # 检查输出目录是否可写
    try:
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        print(f"✅ 输出目录已准备: {config.output_dir}")
    except Exception as e:
        print(f"错误: 无法创建输出目录 {config.output_dir}: {e}")
        return False

    # 检查临时目录是否可写
    try:
        Path(config.temp_dir).mkdir(parents=True, exist_ok=True)
        print(f"✅ 临时目录已准备: {config.temp_dir}")
    except Exception as e:
        print(f"错误: 无法创建临时目录 {config.temp_dir}: {e}")
        return False

    # 检查外部工具路径（仅警告，不阻止启动）
    check_external_tools_with_warnings(config)

    return True

def check_external_tools_with_warnings(config):
    """检查外部工具路径并给出警告（不阻止程序启动）"""
    warnings = []

    # 检查 yt-dlp 是否存在
    if not os.path.exists(config.yt_dlp_path):
        warnings.append(f"⚠️  yt-dlp 未找到: {config.yt_dlp_path}")
    else:
        print(f"✅ yt-dlp 已找到: {config.yt_dlp_path}")

    # 检查 BBDown 是否存在
    if hasattr(config, 'bbdown_path') and config.bbdown_path:
        if not os.path.exists(config.bbdown_path):
            warnings.append(f"⚠️  BBDown 未找到: {config.bbdown_path}")
        else:
            print(f"✅ BBDown 已找到: {config.bbdown_path}")

    # 检查 Whisper 虚拟环境是否存在
    whisper_python = os.path.join(config.whisper_venv_path, 'Scripts', 'python.exe')
    if not os.path.exists(whisper_python):
        warnings.append(f"⚠️  Whisper 环境未找到: {config.whisper_venv_path}")
    else:
        print(f"✅ Whisper 环境已找到: {config.whisper_venv_path}")

    if warnings:
        print("\n📋 配置提醒:")
        for warning in warnings:
            print(f"   {warning}")
        print("\n💡 提示: 程序可以正常启动，请在使用相关功能前配置正确的工具路径。")
        print("   您可以在程序界面中修改配置文件路径设置。")
    else:
        print("\n✅ 所有外部工具路径配置正确！")


def setup_environment():
    """设置运行环境"""
    # 设置日志
    logger = setup_logging()
    logger.info("StreamScribe 启动")
    
    # 清理旧的临时文件
    try:
        config = get_config()
        clean_temp_files(config.temp_dir)
        logger.info("已清理旧的临时文件")
    except Exception as e:
        logger.warning(f"清理临时文件失败: {e}")


def main():
    """主函数"""
    print("StreamScribe - 智能视频文稿提取工具")
    print("=" * 50)
    
    # 检查依赖项
    print("检查依赖项...")
    if not check_dependencies():
        print("\n依赖项检查失败，程序退出。")
        # 在GUI模式下不使用input()，避免PyInstaller打包问题
        import tkinter.messagebox as msgbox
        msgbox.showerror("依赖项检查失败", "依赖项检查失败，程序无法启动。\n请检查配置文件中的路径设置。")
        sys.exit(1)
    
    print("依赖项检查通过。")
    
    # 设置环境
    print("初始化环境...")
    setup_environment()
    
    # 创建并运行 GUI
    try:
        print("启动紧凑版用户界面...")
        app = StreamScribeCompactUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n用户中断，程序退出。")
    except Exception as e:
        print(f"\n程序运行时发生错误: {e}")
        logging.error(f"程序运行时发生错误: {e}", exc_info=True)
        # 在GUI模式下不使用input()，避免PyInstaller打包问题
        import tkinter.messagebox as msgbox
        msgbox.showerror("程序错误", f"程序运行时发生错误:\n{e}\n\n请查看日志文件获取详细信息。")
        sys.exit(1)
    
    print("程序正常退出。")


if __name__ == "__main__":
    main()
