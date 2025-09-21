"""
UI界面布局模块

使用 CustomTkinter 创建现代化的用户界面。
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import subprocess
import re
import sys
import platform
from pathlib import Path
from core.config import get_config
from core.manager import TaskManager


def detect_system_theme():
    """
    检测系统主题（深色/浅色）

    Returns:
        str: "dark" 或 "light"
    """
    system = platform.system()

    if system == "Windows":
        try:
            import winreg
            # 检查Windows注册表中的主题设置
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")

            # AppsUseLightTheme: 0 = 深色, 1 = 浅色
            apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)

            return "light" if apps_use_light_theme else "dark"

        except Exception:
            # 如果无法读取注册表，默认返回深色
            return "dark"

    elif system == "Darwin":  # macOS
        try:
            import subprocess
            # 使用 defaults 命令检查 macOS 主题
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True
            )

            # 如果返回 "Dark"，则是深色主题
            return "dark" if result.stdout.strip() == "Dark" else "light"

        except Exception:
            # 如果命令失败，默认返回浅色（macOS默认）
            return "light"

    elif system == "Linux":
        try:
            # 尝试检测 GNOME/KDE 主题设置
            import subprocess

            # 尝试 GNOME
            try:
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True,
                    text=True
                )
                theme_name = result.stdout.strip().lower()
                if "dark" in theme_name:
                    return "dark"
            except:
                pass

            # 尝试检查环境变量
            if os.environ.get("GTK_THEME", "").lower().find("dark") != -1:
                return "dark"

            return "light"

        except Exception:
            return "light"

    # 其他系统默认返回深色
    return "dark"


class StreamScribeUI:
    """StreamScribe 用户界面类"""
    
    def __init__(self):
        """初始化用户界面"""
        self.config = get_config()
        self.task_manager = TaskManager()
        self.processing = False
        self.current_mode = "url"  # "url" 或 "file"
        self.selected_files = []
        self.current_theme = "auto"  # 当前主题模式

        # 检测并设置系统主题
        self.setup_system_theme()

        self.setup_ui()

    def setup_system_theme(self):
        """设置系统主题"""
        try:
            # 获取配置的主题模式
            theme_mode = self.config.theme_mode
            self.current_theme = theme_mode

            print(f"配置的主题模式: {theme_mode}")

            # 根据配置应用主题
            if theme_mode == "auto":
                # 自动跟随系统主题
                system_theme = detect_system_theme()
                print(f"检测到系统主题: {system_theme}")
                ctk.set_appearance_mode(system_theme)
            else:
                # 使用指定的主题
                print(f"使用指定主题: {theme_mode}")
                ctk.set_appearance_mode(theme_mode)

            # 设置颜色主题
            ctk.set_default_color_theme("blue")

        except Exception as e:
            print(f"设置主题失败，使用默认主题: {e}")
            # 如果设置失败，使用系统默认
            ctk.set_appearance_mode("system")
            ctk.set_default_color_theme("blue")

    def start_theme_monitoring(self):
        """启动主题监控（仅在自动模式下生效）"""
        try:
            # 检查系统主题变化的函数
            def check_theme_change():
                try:
                    # 只有在自动模式下才进行主题检测
                    if self.current_theme == "auto":
                        current_system_theme = detect_system_theme()
                        current_ctk_mode = ctk.get_appearance_mode()

                        # 如果系统主题发生变化，更新界面
                        if ((current_system_theme == "dark" and current_ctk_mode == "Light") or
                            (current_system_theme == "light" and current_ctk_mode == "Dark")):

                            print(f"🔄 自动模式：检测到系统主题变化: {current_system_theme}")
                            if current_system_theme == "dark":
                                ctk.set_appearance_mode("dark")
                            else:
                                ctk.set_appearance_mode("light")
                    # 如果不是自动模式，不进行任何主题检测
                    # else:
                    #     print(f"🔒 手动模式({self.current_theme})：跳过主题检测")

                except Exception as e:
                    print(f"主题监控错误: {e}")

                # 30秒后再次检查（但只有自动模式才会实际执行检测）
                self.root.after(30000, check_theme_change)

            # 启动监控
            self.root.after(30000, check_theme_change)

        except Exception as e:
            print(f"启动主题监控失败: {e}")
        
    def setup_ui(self):
        """设置用户界面"""
        # 注意：主题已在 setup_system_theme 中设置，这里不再重复设置

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title(self.config.app_title)
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.root.minsize(600, 500)  # 设置最小窗口大小

        # 设置窗口图标（如果有的话）
        # self.root.iconbitmap("icon.ico")

        # 启动主题监控（可选功能）
        self.start_theme_monitoring()
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 创建紧凑的界面布局
        self.create_compact_interface()

    def create_compact_interface(self):
        """创建紧凑实用的界面布局"""
        # 1. 顶部标题区域（紧凑）
        self.create_header_section()

        # 2. 处理模式选择（突出显示）
        self.create_mode_section()

        # 3. 输入区域（URL/文件）
        self.create_input_section()

        # 4. 设置和控制区域（模型选择 + 强制转录 + 开始按钮）
        self.create_settings_control_section()

        # 5. 状态和进度区域
        self.create_status_progress_section()

        # 6. 结果区域（包含复制按钮）
        self.create_result_section()

        # 7. 底部工具栏（主题选择等）
        self.create_bottom_toolbar()

    def create_header_section(self):
        """创建紧凑的标题区域"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 15))

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="StreamScribe",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")

        # 主题选择（移到右上角）
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side="right")

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="主题:",
            font=ctk.CTkFont(size=12)
        )
        theme_label.pack(side="left", padx=(0, 5))

        self.theme_var = ctk.StringVar(value=self.get_theme_display_name())
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["🔄 自动", "🌞 浅色", "🌙 深色"],
            command=self.on_theme_changed,
            width=80,
            height=25
        )
        self.theme_menu.pack(side="left")

    def create_mode_section(self):
        """创建处理模式选择区域"""
        mode_frame = ctk.CTkFrame(self.main_frame)
        mode_frame.pack(fill="x", pady=(0, 10))

        # 模式选择标题
        mode_title = ctk.CTkLabel(
            mode_frame,
            text="处理模式",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        mode_title.pack(pady=(15, 5))

        # 模式选择按钮
        mode_button_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_button_frame.pack(pady=(0, 15))

        self.mode_var = ctk.StringVar(value="url")

        self.url_mode_button = ctk.CTkRadioButton(
            mode_button_frame,
            text="在线视频链接",
            variable=self.mode_var,
            value="url",
            command=self.on_mode_changed,
            font=ctk.CTkFont(size=12)
        )
        self.url_mode_button.pack(side="left", padx=(0, 20))

        self.file_mode_button = ctk.CTkRadioButton(
            mode_button_frame,
            text="本地文件",
            variable=self.mode_var,
            value="file",
            command=self.on_mode_changed,
            font=ctk.CTkFont(size=12)
        )
        self.file_mode_button.pack(side="left")

    def create_input_section(self):
        """创建输入区域"""
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", pady=(0, 10))

        # URL输入区域
        self.url_input_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.url_input_frame.pack(fill="x", padx=15, pady=15)

        url_label = ctk.CTkLabel(
            self.url_input_frame,
            text="视频链接:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        url_label.pack(anchor="w", pady=(0, 5))

        self.url_entry = ctk.CTkTextbox(
            self.url_input_frame,
            height=60,
            font=ctk.CTkFont(size=11)
        )
        self.url_entry.pack(fill="x", pady=(0, 5))

        # 设置占位符
        self.url_placeholder_text = "请输入视频链接，支持 YouTube 和 B站，可批量处理..."
        self.url_entry_has_placeholder = True
        self._set_url_placeholder()

        # 绑定焦点事件
        self.url_entry.bind("<FocusIn>", self._on_url_entry_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_entry_focus_out)
        self.url_entry.bind("<KeyPress>", self._on_url_entry_key_press)

        # 文件选择区域
        self.file_input_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")

        file_label = ctk.CTkLabel(
            self.file_input_frame,
            text="选择文件:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        file_label.pack(anchor="w", pady=(0, 5))

        file_button_frame = ctk.CTkFrame(self.file_input_frame, fg_color="transparent")
        file_button_frame.pack(fill="x", pady=(0, 5))

        self.select_files_button = ctk.CTkButton(
            file_button_frame,
            text="选择音频/视频文件",
            command=self.select_files,
            width=150,
            height=30
        )
        self.select_files_button.pack(side="left")

        self.clear_files_button = ctk.CTkButton(
            file_button_frame,
            text="清除",
            command=self.clear_selected_files,
            width=60,
            height=30
        )
        self.clear_files_button.pack(side="left", padx=(10, 0))

        # 文件列表显示
        self.file_list_label = ctk.CTkLabel(
            self.file_input_frame,
            text="未选择文件",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.file_list_label.pack(anchor="w")

        # 初始化文件相关变量
        self.selected_files = []
        self.current_mode = "url"

    def create_settings_control_section(self):
        """创建设置和控制区域"""
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(fill="x", pady=(0, 10))

        # 左侧：模型设置
        left_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=(15, 5), pady=15)

        # 模型选择
        model_label = ctk.CTkLabel(
            left_frame,
            text="AI转录模型:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        model_label.pack(anchor="w", pady=(0, 5))

        model_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        model_container.pack(fill="x", pady=(0, 10))

        self.model_var = ctk.StringVar(value=self.config.whisper_model)
        self.model_menu = ctk.CTkOptionMenu(
            model_container,
            variable=self.model_var,
            values=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
            command=self.on_model_changed,
            width=120,
            height=30
        )
        self.model_menu.pack(side="left")

        # 模型信息
        self.model_info_label = ctk.CTkLabel(
            model_container,
            text=self.get_model_info(self.config.whisper_model),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.model_info_label.pack(side="left", padx=(10, 0))

        # 强制转录模式
        force_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        force_frame.pack(fill="x")

        self.force_transcribe_var = ctk.BooleanVar(value=self.config.force_transcribe_mode)
        self.force_transcribe_checkbox = ctk.CTkCheckBox(
            force_frame,
            text="强制转录模式",
            variable=self.force_transcribe_var,
            command=self.on_force_transcribe_changed,
            font=ctk.CTkFont(size=11)
        )
        self.force_transcribe_checkbox.pack(side="left")

        self.force_transcribe_info = ctk.CTkLabel(
            force_frame,
            text="无视字幕，强制AI转录",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        self.force_transcribe_info.pack(side="left", padx=(5, 0))

        # 右侧：控制按钮
        right_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=(5, 15), pady=15)

        # 开始处理按钮（突出显示）
        self.start_button = ctk.CTkButton(
            right_frame,
            text="开始处理",
            command=self.start_processing,
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(pady=(0, 10))

        # 清除按钮
        self.clear_button = ctk.CTkButton(
            right_frame,
            text="清除",
            command=self.clear_all,
            width=100,
            height=30,
            fg_color="gray",
            hover_color="dark gray"
        )
        self.clear_button.pack()

        # 初始化强制转录模式状态显示
        self.on_force_transcribe_changed()

    def create_status_progress_section(self):
        """创建状态和进度区域"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", pady=(0, 10))

        # 状态标签
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(fill="x", padx=15, pady=(15, 5))

        status_label = ctk.CTkLabel(
            status_container,
            text="状态:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        status_label.pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_container,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=(10, 0))

        # 进度条
        progress_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=15, pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(progress_container)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        # 处理状态标志
        self.processing = False

    def create_result_section(self):
        """创建结果显示区域"""
        result_frame = ctk.CTkFrame(self.main_frame)
        result_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 结果标题和操作按钮
        result_header = ctk.CTkFrame(result_frame, fg_color="transparent")
        result_header.pack(fill="x", padx=15, pady=(15, 5))

        result_title = ctk.CTkLabel(
            result_header,
            text="处理结果:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        result_title.pack(side="left")

        # 操作按钮组
        button_frame = ctk.CTkFrame(result_header, fg_color="transparent")
        button_frame.pack(side="right")

        self.copy_button = ctk.CTkButton(
            button_frame,
            text="复制文本",
            command=self.copy_result_text,
            width=80,
            height=25,
            state="disabled"
        )
        self.copy_button.pack(side="left", padx=(0, 5))

        self.open_file_button = ctk.CTkButton(
            button_frame,
            text="打开文件",
            command=self.open_result_file,
            width=80,
            height=25,
            state="disabled"
        )
        self.open_file_button.pack(side="left")

        # 结果文本框
        self.result_textbox = ctk.CTkTextbox(
            result_frame,
            height=150,
            font=ctk.CTkFont(size=11)
        )
        self.result_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 初始化结果相关变量
        self.current_transcript_file = None
        self.processed_results = []  # 存储多个处理结果

    def create_bottom_toolbar(self):
        """创建底部工具栏"""
        toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        toolbar_frame.pack(fill="x", pady=(0, 10))

        # 版本信息
        version_label = ctk.CTkLabel(
            toolbar_frame,
            text="StreamScribe v1.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack(side="left", padx=(15, 0))

        # 状态信息
        info_label = ctk.CTkLabel(
            toolbar_frame,
            text="支持 YouTube、B站 | AI转录技术",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.pack(side="right", padx=(0, 15))

    def copy_result_text(self):
        """复制结果文本到剪贴板"""
        try:
            if not self.processed_results:
                # 如果没有处理结果，复制当前文本框内容
                content = self.result_textbox.get("1.0", "end").strip()
                if content:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(content)
                    self.update_status("文本已复制到剪贴板")
                else:
                    self.update_status("没有可复制的内容")
                return

            # 如果有多个处理结果，按照 标题+内容 的格式拼接
            if len(self.processed_results) == 1:
                # 单个结果，直接复制内容
                result = self.processed_results[0]
                content = result.get('content', '')
            else:
                # 多个结果，按照 标题+内容 格式拼接
                content_parts = []
                for result in self.processed_results:
                    title = result.get('title', '未知标题')
                    text = result.get('content', '')
                    content_parts.append(f"=== {title} ===\n{text}")
                content = "\n\n".join(content_parts)

            if content:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.update_status(f"已复制 {len(self.processed_results)} 个结果到剪贴板")
            else:
                self.update_status("没有可复制的内容")

        except Exception as e:
            self.update_status(f"复制失败: {str(e)}")

    def create_url_input_section(self):
        """创建输入区域（支持URL和本地文件）"""
        # 输入框架
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 模式选择区域
        mode_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(20, 10))

        # 模式选择标签
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="处理模式:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        mode_label.pack(side="left")

        # 模式选择按钮
        self.mode_var = ctk.StringVar(value="url")

        self.url_mode_radio = ctk.CTkRadioButton(
            mode_frame,
            text="在线视频链接",
            variable=self.mode_var,
            value="url",
            command=self.on_mode_changed
        )
        self.url_mode_radio.pack(side="left", padx=(20, 10))

        self.file_mode_radio = ctk.CTkRadioButton(
            mode_frame,
            text="本地文件",
            variable=self.mode_var,
            value="file",
            command=self.on_mode_changed
        )
        self.file_mode_radio.pack(side="left", padx=(10, 0))

        # URL输入区域
        self.url_input_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        self.url_input_frame.pack(fill="x", padx=20, pady=(0, 10))

        url_label = ctk.CTkLabel(
            self.url_input_frame,
            text="视频链接 (支持 YouTube、B站，批量用回车或空格分隔):",
            font=ctk.CTkFont(size=12)
        )
        url_label.pack(anchor="w", pady=(0, 5))

        self.url_entry = ctk.CTkTextbox(
            self.url_input_frame,
            height=80,
            font=ctk.CTkFont(size=11)
        )
        self.url_entry.pack(fill="x", pady=(0, 10))

        # 设置占位符
        self.url_placeholder_text = "请输入视频链接，支持 YouTube 和 B站，可批量处理..."
        self.url_entry_has_placeholder = True
        self._set_url_placeholder()

        # 绑定焦点事件
        self.url_entry.bind("<FocusIn>", self._on_url_entry_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_entry_focus_out)
        self.url_entry.bind("<KeyPress>", self._on_url_entry_key_press)

        # 本地文件区域
        self.file_input_frame = ctk.CTkFrame(input_frame, fg_color="transparent")

        # 动态生成支持格式的显示文本
        audio_formats = ', '.join(self.config.supported_audio_formats)
        video_formats = ', '.join(self.config.supported_video_formats)

        file_label = ctk.CTkLabel(
            self.file_input_frame,
            text=f"本地文件 (支持音频: {audio_formats} | 视频: {video_formats}):",
            font=ctk.CTkFont(size=12)
        )
        file_label.pack(anchor="w", pady=(0, 5))

        # 文件选择按钮区域
        file_buttons_frame = ctk.CTkFrame(self.file_input_frame, fg_color="transparent")
        file_buttons_frame.pack(fill="x", pady=(0, 10))

        self.select_files_btn = ctk.CTkButton(
            file_buttons_frame,
            text="📁 选择文件",
            width=120,
            height=35,
            command=self.select_files
        )
        self.select_files_btn.pack(side="left", padx=(0, 10))

        self.clear_files_btn = ctk.CTkButton(
            file_buttons_frame,
            text="🗑️ 清空",
            width=80,
            height=35,
            command=self.clear_files
        )
        self.clear_files_btn.pack(side="left")

        # 文件列表显示
        self.file_list_label = ctk.CTkLabel(
            self.file_input_frame,
            text="拖拽文件到此处，或点击上方按钮选择文件",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.file_list_label.pack(anchor="w")

        # 设置初始模式
        self.on_mode_changed()

    def _set_url_placeholder(self):
        """设置URL输入框的占位符"""
        self.url_entry.delete("1.0", "end")
        self.url_entry.insert("1.0", self.url_placeholder_text)
        self.url_entry.configure(text_color="gray")
        self.url_entry_has_placeholder = True

    def _clear_url_placeholder(self):
        """清除URL输入框的占位符"""
        if self.url_entry_has_placeholder:
            self.url_entry.delete("1.0", "end")
            self.url_entry.configure(text_color=("gray10", "gray90"))  # 恢复正常颜色
            self.url_entry_has_placeholder = False

    def _on_url_entry_focus_in(self, event):
        """URL输入框获得焦点时的处理"""
        self._clear_url_placeholder()

    def _on_url_entry_focus_out(self, event):
        """URL输入框失去焦点时的处理"""
        content = self.url_entry.get("1.0", "end").strip()
        if not content:
            self._set_url_placeholder()

    def _on_url_entry_key_press(self, event):
        """URL输入框按键时的处理"""
        # 如果当前显示占位符，任何按键都会清除占位符
        if self.url_entry_has_placeholder:
            # 延迟清除占位符，让按键事件先处理
            self.url_entry.after(1, self._clear_url_placeholder)

    def _get_url_text(self):
        """获取URL输入框的实际文本（排除占位符）"""
        if self.url_entry_has_placeholder:
            return ""
        return self.url_entry.get("1.0", "end").strip()

    def create_model_selection_section(self):
        """创建模型选择区域"""
        # 模型选择框架
        model_frame = ctk.CTkFrame(self.main_frame)
        model_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 模型选择标签
        model_label = ctk.CTkLabel(
            model_frame,
            text="AI转录模型:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        model_label.pack(anchor="w", padx=20, pady=(20, 5))

        # 模型选择容器
        model_container = ctk.CTkFrame(model_frame, fg_color="transparent")
        model_container.pack(fill="x", padx=20, pady=(0, 20))

        # 模型下拉框
        available_models = self.config.get_available_models()
        self.model_combobox = ctk.CTkComboBox(
            model_container,
            values=available_models,
            width=150,
            height=35,
            font=ctk.CTkFont(size=12),
            command=self.on_model_changed
        )
        self.model_combobox.set(self.config.whisper_model)  # 设置默认值
        self.model_combobox.pack(side="left", padx=(0, 10))

        # 模型信息标签
        self.model_info_label = ctk.CTkLabel(
            model_container,
            text=self.get_model_info(self.config.whisper_model),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.model_info_label.pack(side="left", anchor="w")

        # 强制转录模式选项
        force_transcribe_container = ctk.CTkFrame(model_frame, fg_color="transparent")
        force_transcribe_container.pack(fill="x", padx=20, pady=(0, 20))

        # 强制转录模式勾选框
        self.force_transcribe_var = ctk.BooleanVar(value=self.config.force_transcribe_mode)
        self.force_transcribe_checkbox = ctk.CTkCheckBox(
            force_transcribe_container,
            text="强制转录模式 (无视字幕，强制使用AI转录)",
            variable=self.force_transcribe_var,
            font=ctk.CTkFont(size=12),
            command=self.on_force_transcribe_changed
        )
        self.force_transcribe_checkbox.pack(side="left")

        # 强制转录模式说明
        self.force_transcribe_info = ctk.CTkLabel(
            force_transcribe_container,
            text="启用后将跳过字幕检测，直接下载音频进行AI转录",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.force_transcribe_info.pack(side="left", padx=(10, 0))

        # 初始化强制转录模式状态显示
        self.on_force_transcribe_changed()

    def on_model_changed(self, selected_model):
        """模型选择改变时的回调"""
        # 更新模型信息显示
        self.model_info_label.configure(text=self.get_model_info(selected_model))

        # 更新配置（临时更新，不保存到文件）
        self.config.config.set('whisper', 'model', selected_model)

    def on_force_transcribe_changed(self):
        """强制转录模式改变时的回调"""
        force_mode = self.force_transcribe_var.get()

        # 保存到配置文件
        self.config.set_force_transcribe_mode(force_mode)

        # 更新说明文本的颜色来提示用户
        if force_mode:
            self.force_transcribe_info.configure(
                text="✅ 已启用：将跳过字幕检测，直接使用AI转录",
                text_color="#1f8b4c"  # 绿色
            )
        else:
            self.force_transcribe_info.configure(
                text="启用后将跳过字幕检测，直接下载音频进行AI转录",
                text_color="gray"
            )

    def get_model_info(self, model):
        """获取模型信息描述"""
        model_info = {
            'base': '量化: int8 | 速度: 快 | 准确度: 中等 | 显存: 低',
            'small': '量化: int8_float16 | 速度: 较快 | 准确度: 好 | 显存: 中等',
            'medium': '量化: float16 | 速度: 中等 | 准确度: 很好 | 显存: 中等',
            'large-v2': '量化: float16 | 速度: 慢 | 准确度: 极好 | 显存: 高',
            'large-v3': '量化: float16 | 速度: 慢 | 准确度: 最好 | 显存: 高'
        }
        return model_info.get(model, '未知模型')

    def on_mode_changed(self):
        """模式切换回调"""
        mode = self.mode_var.get()
        self.current_mode = mode

        if mode == "url":
            # 显示URL输入区域，隐藏文件输入区域
            self.url_input_frame.pack(fill="x", padx=20, pady=(0, 10))
            self.file_input_frame.pack_forget()
        else:
            # 显示文件输入区域，隐藏URL输入区域
            self.url_input_frame.pack_forget()
            self.file_input_frame.pack(fill="x", padx=20, pady=(0, 10))

    def select_files(self):
        """选择本地文件"""
        # 构建文件类型过滤器
        audio_formats = self.config.supported_audio_formats
        video_formats = self.config.supported_video_formats

        filetypes = [
            ("所有支持的文件", " ".join([f"*.{fmt}" for fmt in audio_formats + video_formats])),
            ("音频文件", " ".join([f"*.{fmt}" for fmt in audio_formats])),
            ("视频文件", " ".join([f"*.{fmt}" for fmt in video_formats])),
            ("所有文件", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="选择要转录的文件",
            filetypes=filetypes
        )

        if files:
            # 验证文件格式
            valid_files = []
            invalid_files = []

            for file_path in files:
                if self._is_supported_file(file_path):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(file_path)

            if invalid_files:
                invalid_names = [os.path.basename(f) for f in invalid_files]
                messagebox.showwarning(
                    "文件格式警告",
                    f"以下文件格式不支持，已跳过:\n{', '.join(invalid_names)}"
                )

            if valid_files:
                self.selected_files.extend(valid_files)
                self.update_file_list_display()

    def clear_files(self):
        """清空选择的文件"""
        self.selected_files.clear()
        self.update_file_list_display()

    def update_file_list_display(self):
        """更新文件列表显示"""
        if not self.selected_files:
            self.file_list_label.configure(
                text="拖拽文件到此处，或点击上方按钮选择文件",
                text_color="gray"
            )
        else:
            file_names = [os.path.basename(f) for f in self.selected_files]
            if len(file_names) <= 5:
                display_text = f"已选择 {len(file_names)} 个文件:\n" + "\n".join(file_names)
            else:
                display_text = f"已选择 {len(file_names)} 个文件:\n" + "\n".join(file_names[:5]) + f"\n... 还有 {len(file_names) - 5} 个文件"

            self.file_list_label.configure(
                text=display_text,
                text_color="white"
            )

    def _is_supported_file(self, file_path):
        """检查文件是否支持"""
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        supported_formats = self.config.get_all_supported_formats()
        return file_ext in supported_formats
    
    def create_control_section(self):
        """创建控制按钮区域"""
        # 控制按钮框架
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 按钮容器
        button_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_container.pack(pady=20)
        
        # 开始按钮
        self.start_button = ctk.CTkButton(
            button_container,
            text="开始处理",
            command=self.start_processing,
            height=40,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", padx=(0, 10))
        
        # 清除按钮
        self.clear_button = ctk.CTkButton(
            button_container,
            text="清除",
            command=self.clear_all,
            height=40,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_button.pack(side="left", padx=(0, 10))
        
        # 打开输出目录按钮
        self.open_dir_button = ctk.CTkButton(
            button_container,
            text="打开输出目录",
            command=self.open_output_directory,
            height=40,
            width=120,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.open_dir_button.pack(side="left")
    
    def create_status_section(self):
        """创建状态显示区域"""
        # 状态框架
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 状态标签
        status_label = ctk.CTkLabel(
            status_frame,
            text="状态:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # 状态文本
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="就绪",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_text.pack(anchor="w", padx=20, pady=(0, 10))
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.set(0)
    
    def create_result_section(self):
        """创建结果显示区域"""
        # 结果框架
        result_frame = ctk.CTkFrame(self.main_frame)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 结果标签
        result_label = ctk.CTkLabel(
            result_frame,
            text="处理结果:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        result_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # 结果文本框
        self.result_textbox = ctk.CTkTextbox(
            result_frame,
            height=150,
            font=ctk.CTkFont(size=11)
        )
        self.result_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 结果按钮框架
        result_button_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        result_button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # 打开文件按钮
        self.open_file_button = ctk.CTkButton(
            result_button_frame,
            text="打开文稿文件",
            command=self.open_transcript_file,
            height=35,
            width=120,
            state="disabled"
        )
        self.open_file_button.pack(side="left", padx=(0, 10))
        
        # 复制文本按钮
        self.copy_button = ctk.CTkButton(
            result_button_frame,
            text="复制文本",
            command=self.copy_result_text,
            height=35,
            width=100,
            state="disabled"
        )
        self.copy_button.pack(side="left")
    
    def create_footer_section(self):
        """创建底部信息区域"""
        # 底部框架
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", padx=20)

        # 支持平台信息
        platform_label = ctk.CTkLabel(
            footer_frame,
            text="支持: YouTube、B站、本地文件",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        platform_label.pack(side="left")

        # 中间区域 - 主题切换按钮
        if self.config.show_theme_switch:
            self.create_theme_switch(footer_frame)

        # 版本信息
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack(side="right")

    def create_theme_switch(self, parent_frame):
        """创建主题切换按钮"""
        # 主题切换容器
        theme_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        theme_frame.pack(side="right", padx=(0, 20))

        # 主题标签
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="主题:",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        theme_label.pack(side="left", padx=(0, 5))

        # 主题切换按钮
        self.theme_switch = ctk.CTkSegmentedButton(
            theme_frame,
            values=["🌙 深色", "🌞 浅色", "🔄 自动"],
            command=self.on_theme_changed,
            width=180,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        self.theme_switch.pack(side="left")

        # 设置当前主题状态
        self.update_theme_switch_state()

    def update_theme_switch_state(self):
        """更新主题切换按钮的状态"""
        theme_map = {
            "dark": "🌙 深色",
            "light": "🌞 浅色",
            "auto": "🔄 自动"
        }

        current_display = theme_map.get(self.current_theme, "🔄 自动")
        self.theme_switch.set(current_display)

    def on_theme_changed(self, value):
        """主题切换回调"""
        try:
            # 映射显示文本到主题值
            theme_map = {
                "🌙 深色": "dark",
                "🌞 浅色": "light",
                "🔄 自动": "auto"
            }

            new_theme = theme_map.get(value, "auto")

            if new_theme != self.current_theme:
                self.current_theme = new_theme

                # 保存到配置文件
                self.config.set_theme_mode(new_theme)

                # 应用新主题
                self.apply_theme(new_theme)

                print(f"主题已切换为: {new_theme}")

        except Exception as e:
            print(f"切换主题失败: {e}")

    def apply_theme(self, theme_mode):
        """应用指定的主题"""
        try:
            if theme_mode == "auto":
                # 自动跟随系统主题
                system_theme = detect_system_theme()
                ctk.set_appearance_mode(system_theme)
                print(f"自动主题: 跟随系统 ({system_theme})")
            else:
                # 使用指定主题
                ctk.set_appearance_mode(theme_mode)
                print(f"手动主题: {theme_mode}")

        except Exception as e:
            print(f"应用主题失败: {e}")
    
    def start_processing(self):
        """开始处理（支持URL和本地文件的批量处理）"""
        if self.processing:
            return

        if self.current_mode == "url":
            # URL模式
            url_text = self._get_url_text()
            if not url_text:
                messagebox.showwarning("警告", "请输入视频链接")
                return

            # 解析多个URL（用回车或空格分隔）
            urls = self._parse_urls(url_text)
            if not urls:
                messagebox.showwarning("警告", "未找到有效的视频链接")
                return

            # 检查是否超过批量限制
            if len(urls) > self.config.max_batch_files:
                messagebox.showwarning(
                    "批量限制",
                    f"最多支持同时处理 {self.config.max_batch_files} 个链接，当前选择了 {len(urls)} 个"
                )
                return

            self._start_smart_batch_url_processing(urls)

        else:
            # 文件模式
            if not self.selected_files:
                messagebox.showwarning("警告", "请选择要处理的文件")
                return

            # 检查是否超过批量限制
            if len(self.selected_files) > self.config.max_batch_files:
                messagebox.showwarning(
                    "批量限制",
                    f"最多支持同时处理 {self.config.max_batch_files} 个文件，当前选择了 {len(self.selected_files)} 个"
                )
                return

            self._start_batch_file_processing(self.selected_files)

    def _parse_urls(self, text):
        """解析文本中的URL列表"""
        # 用回车、空格、制表符分隔
        urls = re.split(r'[\n\r\s\t]+', text.strip())

        # 过滤空字符串和无效URL
        valid_urls = []
        for url in urls:
            url = url.strip()
            if url and self._is_supported_url(url):
                valid_urls.append(url)

        return valid_urls

    def _is_supported_url(self, url):
        """检查URL是否支持"""
        # YouTube 链接
        if 'youtube.com' in url or 'youtu.be' in url:
            return True

        # B站链接
        if 'bilibili.com' in url or 'b23.tv' in url:
            return True

        return False

    def _get_url_platform(self, url):
        """获取URL对应的平台"""
        from core.utils import extract_video_id_from_url
        platform, _ = extract_video_id_from_url(url)
        return platform

    def _start_smart_batch_url_processing(self, urls):
        """智能批量URL处理（按平台分组）"""
        # 按平台分组URL
        platform_groups = {}
        for url in urls:
            platform = self._get_url_platform(url)
            if platform:
                if platform not in platform_groups:
                    platform_groups[platform] = []
                platform_groups[platform].append(url)

        if not platform_groups:
            messagebox.showwarning("警告", "未找到支持的视频链接")
            return

        # 显示分组信息
        group_info = []
        for platform, platform_urls in platform_groups.items():
            platform_name = "YouTube" if platform == "youtube" else "B站" if platform == "bilibili" else platform
            group_info.append(f"{platform_name}: {len(platform_urls)} 个")

        # 设置处理状态
        self.processing = True
        self.start_button.configure(state="disabled", text="智能批量处理中...")
        self.progress_bar.set(0)
        self.result_textbox.delete("1.0", "end")
        self.open_file_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")

        # 显示批量处理信息
        self.update_status(f"开始智能批量处理: {', '.join(group_info)}")

        # 在新线程中处理
        thread = threading.Thread(target=self._process_smart_batch_urls_thread, args=(platform_groups,))
        thread.daemon = True
        thread.start()

    def _process_smart_batch_urls_thread(self, platform_groups):
        """在后台线程中智能批量处理URL"""
        def status_callback(message):
            """状态回调函数"""
            self.root.after(0, lambda: self.update_status(message))

        try:
            all_results = []
            total_success = 0
            total_count = sum(len(urls) for urls in platform_groups.values())

            for platform, urls in platform_groups.items():
                platform_name = "YouTube" if platform == "youtube" else "B站" if platform == "bilibili" else platform
                status_callback(f"正在处理 {platform_name} 链接...")

                # 批量处理同平台的URL
                batch_result = self.task_manager.process_batch_urls(urls, status_callback)

                # 合并结果
                for result in batch_result['results']:
                    result['platform'] = platform_name
                    all_results.append(result)

                total_success += batch_result['success_count']

            # 构建最终结果
            final_result = {
                'success': total_success > 0,
                'total_count': total_count,
                'success_count': total_success,
                'failed_count': total_count - total_success,
                'results': all_results,
                'platform_groups': platform_groups
            }

            # 在主线程中更新UI
            self.root.after(0, lambda: self._handle_smart_batch_processing_result(final_result))

        except Exception as e:
            error_msg = f"智能批量处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self._handle_processing_error(error_msg))

    def _handle_smart_batch_processing_result(self, batch_result):
        """处理智能批量处理结果"""
        self.processing = False
        self.start_button.configure(state="normal", text="开始处理")
        self.progress_bar.set(1.0)

        if batch_result['success']:
            # 显示智能批量处理摘要
            summary = f"智能批量处理完成！\n"
            summary += f"总计: {batch_result['total_count']} 个链接\n"
            summary += f"成功: {batch_result['success_count']} 个\n"
            summary += f"失败: {batch_result['failed_count']} 个\n\n"

            # 按平台显示结果
            current_platform = None
            for result in batch_result['results']:
                platform = result.get('platform', '未知平台')
                if platform != current_platform:
                    summary += f"=== {platform} ===\n"
                    current_platform = platform

                if result['success']:
                    file_name = result.get('video_title', result.get('file_name', '未知视频'))
                    summary += f"✅ {file_name}\n"
                    if result.get('transcript_file'):
                        summary += f"   文稿: {os.path.basename(result['transcript_file'])}\n"
                    summary += f"   方法: {result.get('method', '未知')}\n"
                else:
                    file_name = result.get('video_title', result.get('file_name', '未知视频'))
                    summary += f"❌ {file_name}\n"
                    summary += f"   错误: {result.get('error', '未知错误')}\n"
                summary += "\n"

            self.result_textbox.insert("1.0", summary)

            # 如果有成功的结果，启用相关按钮
            if batch_result['success_count'] > 0:
                self.open_file_button.configure(state="normal")
                self.copy_button.configure(state="normal")

                # 如果只有一个成功的结果，设置为当前结果文件
                success_results = [r for r in batch_result['results'] if r['success']]
                if len(success_results) == 1:
                    self.current_result_file = success_results[0]['transcript_file']

            self.update_status("智能批量处理完成！")

        else:
            self.result_textbox.insert("1.0", "智能批量处理失败，所有链接都处理失败。")
            self.update_status("智能批量处理失败")

    def _start_batch_url_processing(self, urls):
        """开始批量URL处理"""
        # 设置处理状态
        self.processing = True
        self.start_button.configure(state="disabled", text="批量处理中...")
        self.progress_bar.set(0)
        self.result_textbox.delete("1.0", "end")
        self.open_file_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")

        # 显示批量处理信息
        self.update_status(f"开始批量处理 {len(urls)} 个视频链接...")

        # 在新线程中处理
        thread = threading.Thread(target=self._process_batch_urls_thread, args=(urls,))
        thread.daemon = True
        thread.start()

    def _start_batch_file_processing(self, file_paths):
        """开始批量文件处理"""
        # 设置处理状态
        self.processing = True
        self.start_button.configure(state="disabled", text="批量处理中...")
        self.progress_bar.set(0)
        self.result_textbox.delete("1.0", "end")
        self.open_file_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")

        # 显示批量处理信息
        self.update_status(f"开始批量处理 {len(file_paths)} 个本地文件...")

        # 在新线程中处理
        thread = threading.Thread(target=self._process_batch_files_thread, args=(file_paths,))
        thread.daemon = True
        thread.start()

    def _process_batch_urls_thread(self, urls):
        """在后台线程中批量处理URL"""
        def status_callback(message):
            """状态回调函数"""
            self.root.after(0, lambda: self.update_status(message))

        try:
            result = self.task_manager.process_batch_urls(urls, status_callback)

            # 在主线程中更新UI
            self.root.after(0, lambda: self._handle_batch_processing_result(result))

        except Exception as e:
            error_msg = f"批量处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self._handle_processing_error(error_msg))

    def _process_batch_files_thread(self, file_paths):
        """在后台线程中批量处理文件"""
        def status_callback(message):
            """状态回调函数"""
            self.root.after(0, lambda: self.update_status(message))

        try:
            result = self.task_manager.process_batch_files(file_paths, status_callback)

            # 在主线程中更新UI
            self.root.after(0, lambda: self._handle_batch_processing_result(result))

        except Exception as e:
            error_msg = f"批量处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self._handle_processing_error(error_msg))

    def _handle_batch_processing_result(self, batch_result):
        """处理批量处理结果"""
        self.processing = False
        self.start_button.configure(state="normal", text="开始处理")
        self.progress_bar.set(1.0)

        if batch_result['success']:
            # 显示批量处理摘要
            summary = f"批量处理完成！\n"
            summary += f"总计: {batch_result['total_count']} 个\n"
            summary += f"成功: {batch_result['success_count']} 个\n"
            summary += f"失败: {batch_result['failed_count']} 个\n\n"

            # 显示每个文件的结果
            for i, result in enumerate(batch_result['results'], 1):
                if result['success']:
                    file_name = result.get('file_name', f'文件{i}')
                    summary += f"✅ {file_name}\n"
                    if result.get('transcript_file'):
                        summary += f"   文稿: {os.path.basename(result['transcript_file'])}\n"
                else:
                    file_name = result.get('file_name', f'文件{i}')
                    summary += f"❌ {file_name}\n"
                    summary += f"   错误: {result.get('error', '未知错误')}\n"
                summary += "\n"

            self.result_textbox.insert("1.0", summary)

            # 如果有成功的结果，启用相关按钮
            if batch_result['success_count'] > 0:
                self.open_file_button.configure(state="normal")
                self.copy_button.configure(state="normal")

                # 如果只有一个成功的结果，设置为当前结果文件
                success_results = [r for r in batch_result['results'] if r['success']]
                if len(success_results) == 1:
                    self.current_result_file = success_results[0]['transcript_file']

            self.update_status("批量处理完成！")

        else:
            self.result_textbox.insert("1.0", "批量处理失败，所有文件都处理失败。")
            self.update_status("批量处理失败")
    
    def _process_video_thread(self, url):
        """在后台线程中处理视频"""
        from core.manager import TaskManager
        
        def status_callback(message):
            """状态回调函数"""
            self.root.after(0, lambda: self.update_status(message))
        
        try:
            manager = TaskManager()
            result = manager.process_url(url, status_callback)
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self._handle_processing_result(result))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self._handle_processing_error(error_msg))
    
    def _handle_processing_result(self, result):
        """处理结果回调"""
        self.processing = False
        self.start_button.configure(state="normal", text="开始处理")
        self.progress_bar.set(1.0)
        
        if result['success']:
            # 成功处理
            self.update_status("处理完成！")
            
            # 显示结果信息
            info_text = f"视频标题: {result.get('video_title', 'Unknown')}\n"
            info_text += f"平台: {result.get('platform', 'Unknown').upper()}\n"
            info_text += f"处理方式: {'字幕' if result.get('method') == 'subtitle' else 'AI转录'}\n"
            info_text += f"文稿文件: {result.get('transcript_file', 'Unknown')}\n\n"
            
            # 读取并显示文稿内容预览
            try:
                with open(result['transcript_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:500] + "..." if len(content) > 500 else content
                    info_text += f"文稿预览:\n{preview}"
            except:
                info_text += "无法读取文稿内容"
            
            self.result_textbox.insert("1.0", info_text)
            self.open_file_button.configure(state="normal")
            self.copy_button.configure(state="normal")
            
            # 保存文件路径
            self.current_transcript_file = result['transcript_file']
            
            # 如果配置了自动打开，则打开文件
            if self.config.auto_open_result:
                self.open_transcript_file()
                
        else:
            # 处理失败
            error_msg = result.get('error', '未知错误')
            self.update_status(f"处理失败: {error_msg}")
            self.result_textbox.insert("1.0", f"错误: {error_msg}")
    
    def _handle_processing_error(self, error_msg):
        """处理错误回调"""
        self.processing = False
        self.start_button.configure(state="normal", text="开始处理")
        self.progress_bar.set(0)
        self.update_status("处理失败")
        self.result_textbox.insert("1.0", error_msg)
    
    def update_status(self, message):
        """更新状态显示"""
        self.status_text.configure(text=message)
    
    def clear_all(self):
        """清除所有内容"""
        if self.processing:
            return

        # 清除URL输入框并恢复占位符
        self._set_url_placeholder()

        # 清除结果文本框
        self.result_textbox.delete("1.0", "end")

        # 清除选择的文件（如果在文件模式）
        self.selected_files.clear()
        self.update_file_list_display()

        # 重置强制转录模式
        self.force_transcribe_var.set(False)
        self.on_force_transcribe_changed()

        # 重置UI状态
        self.update_status("就绪")
        self.progress_bar.set(0)
        self.open_file_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.current_transcript_file = None
    
    def open_output_directory(self):
        """打开输出目录"""
        try:
            output_dir = self.config.output_dir
            if os.path.exists(output_dir):
                os.startfile(output_dir)
            else:
                messagebox.showwarning("警告", f"输出目录不存在: {output_dir}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开输出目录: {str(e)}")
    
    def open_transcript_file(self):
        """打开文稿文件"""
        if hasattr(self, 'current_transcript_file') and self.current_transcript_file:
            try:
                os.startfile(self.current_transcript_file)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
    
    def copy_result_text(self):
        """复制结果文本到剪贴板"""
        try:
            text = self.result_textbox.get("1.0", "end-1c")
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("信息", "文本已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()
