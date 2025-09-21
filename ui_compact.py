#!/usr/bin/env python3
"""
StreamScribe 紧凑UI界面

重新设计的紧凑实用界面，突出最常用功能：
- 处理模式选择
- 视频链接框
- 开始处理按钮
- 强制转录按钮
- 状态进度条
- 复制按钮（智能复制转录文本）
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import platform
import os
import threading
import datetime
from core.config import get_config
from core.manager import TaskManager


class DebugWindow:
    """调试窗口类"""

    def __init__(self, parent):
        """初始化调试窗口"""
        self.parent = parent
        self.window = None
        self.text_widget = None
        self.is_visible = False

    def show(self):
        """显示调试窗口"""
        if self.window is None:
            self._create_window()

        if not self.is_visible:
            self.window.deiconify()
            self.is_visible = True

    def hide(self):
        """隐藏调试窗口"""
        if self.window and self.is_visible:
            self.window.withdraw()
            self.is_visible = False

    def _create_window(self):
        """创建调试窗口"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("StreamScribe - 调试窗口")
        self.window.geometry("800x600")

        # 设置窗口位置（在主窗口右侧）
        parent_x = self.parent.winfo_x()
        parent_width = self.parent.winfo_width()
        self.window.geometry(f"+{parent_x + parent_width + 10}+{self.parent.winfo_y()}")

        # 创建文本框
        self.text_widget = ctk.CTkTextbox(
            self.window,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加清除按钮
        clear_button = ctk.CTkButton(
            self.window,
            text="清除日志",
            command=self.clear_log,
            width=100,
            height=30
        )
        clear_button.pack(pady=(0, 10))

        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # 初始化时隐藏窗口
        self.window.withdraw()

    def add_message(self, message):
        """添加调试信息"""
        if self.text_widget:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"

            self.text_widget.insert("end", formatted_message)
            self.text_widget.see("end")  # 自动滚动到底部

    def clear_log(self):
        """清除日志"""
        if self.text_widget:
            self.text_widget.delete("1.0", "end")

    def on_close(self):
        """窗口关闭时的处理"""
        self.hide()
        # 同时取消调试模式勾选
        if hasattr(self.parent, 'debug_mode_var'):
            # 这里需要通过父窗口来访问
            for widget in self.parent.winfo_children():
                if hasattr(widget, 'debug_mode_var'):
                    widget.debug_mode_var.set(False)
                    widget.on_debug_mode_changed()
                    break


def detect_system_theme():
    """检测系统主题（深色/浅色）"""
    system = platform.system()

    if system == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if apps_use_light_theme else "dark"
        except Exception:
            return "dark"

    elif system == "Darwin":  # macOS
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True
            )
            return "dark" if result.stdout.strip() == "Dark" else "light"
        except Exception:
            return "light"

    elif system == "Linux":
        try:
            import subprocess
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

            if os.environ.get("GTK_THEME", "").lower().find("dark") != -1:
                return "dark"
            return "light"
        except Exception:
            return "light"

    return "dark"


class StreamScribeCompactUI:
    """StreamScribe 紧凑UI界面"""
    
    def __init__(self):
        """初始化UI"""
        # 获取配置
        self.config = get_config()

        # 设置初始化标志，防止初始化时触发配置保存
        self._initializing = True

        # 设置主题
        self.setup_theme()

        # 创建主窗口
        self.setup_window()

        # 创建任务管理器
        self.manager = TaskManager()

        # 设置调试回调
        self.manager.set_debug_callback(self.log_debug_message)

        # 初始化变量
        self.processing = False
        self.current_transcript_file = None
        self.processed_results = []
        self.selected_files = []
        self.debug_window = None

        # 创建界面
        self.create_interface()

        # 初始化完成，允许配置保存
        self._initializing = False

        # 启动主题监控
        self.start_theme_monitoring()
    
    def setup_theme(self):
        """设置主题"""
        try:
            theme_mode = self.config.theme_mode
            self.current_theme = theme_mode
            
            if theme_mode == "auto":
                system_theme = detect_system_theme()
                ctk.set_appearance_mode(system_theme)
            else:
                ctk.set_appearance_mode(theme_mode)
            
            ctk.set_default_color_theme("blue")
        except Exception as e:
            print(f"设置主题失败: {e}")
            ctk.set_appearance_mode("system")
            ctk.set_default_color_theme("blue")
    
    def setup_window(self):
        """设置主窗口"""
        self.root = ctk.CTk()
        self.root.title(self.config.app_title)
        self.root.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.root.minsize(650, 600)
        
        # 启动主题监控
        self.start_theme_monitoring()
    
    def start_theme_monitoring(self):
        """启动主题监控（仅在自动模式下生效）"""
        try:
            def check_theme_change():
                try:
                    if self.current_theme == "auto":
                        current_system_theme = detect_system_theme()
                        current_ctk_mode = ctk.get_appearance_mode()

                        if ((current_system_theme == "dark" and current_ctk_mode == "Light") or
                            (current_system_theme == "light" and current_ctk_mode == "Dark")):

                            print(f"🔄 自动模式：检测到系统主题变化: {current_system_theme}")
                            if current_system_theme == "dark":
                                ctk.set_appearance_mode("dark")
                            else:
                                ctk.set_appearance_mode("light")

                except Exception as e:
                    print(f"主题监控错误: {e}")

                self.root.after(30000, check_theme_change)

            self.root.after(30000, check_theme_change)

        except Exception as e:
            print(f"启动主题监控失败: {e}")
    
    def create_interface(self):
        """创建紧凑界面"""
        # 主容器
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 1. 标题和主题选择
        self.create_header(main_container)
        
        # 2. 处理模式选择
        self.create_mode_selection(main_container)
        
        # 3. 输入区域
        self.create_input_area(main_container)
        
        # 4. 设置和控制区域
        self.create_control_area(main_container)
        
        # 5. 状态和进度
        self.create_status_area(main_container)
        
        # 6. 结果区域
        self.create_result_area(main_container)
        
        # 7. 底部信息
        self.create_footer(main_container)
        
        # 设置初始模式
        self.on_mode_changed()
    
    def create_header(self, parent):
        """创建标题和主题选择"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 15))
        
        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="StreamScribe",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left")
        
        # 主题选择
        theme_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_frame.pack(side="right")
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="主题:",
            font=ctk.CTkFont(size=11)
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
    
    def create_mode_selection(self, parent):
        """创建处理模式选择"""
        mode_frame = ctk.CTkFrame(parent)
        mode_frame.pack(fill="x", pady=(0, 10))
        
        mode_title = ctk.CTkLabel(
            mode_frame,
            text="处理模式",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        mode_title.pack(pady=(12, 8))
        
        button_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 12))
        
        self.mode_var = ctk.StringVar(value="url")
        
        self.url_mode_button = ctk.CTkRadioButton(
            button_frame,
            text="在线视频链接",
            variable=self.mode_var,
            value="url",
            command=self.on_mode_changed,
            font=ctk.CTkFont(size=12)
        )
        self.url_mode_button.pack(side="left", padx=(0, 20))
        
        self.file_mode_button = ctk.CTkRadioButton(
            button_frame,
            text="本地文件",
            variable=self.mode_var,
            value="file",
            command=self.on_mode_changed,
            font=ctk.CTkFont(size=12)
        )
        self.file_mode_button.pack(side="left")
    
    def create_input_area(self, parent):
        """创建输入区域"""
        self.input_frame = ctk.CTkFrame(parent)
        self.input_frame.pack(fill="x", pady=(0, 10))

        # URL输入区域
        self.url_input_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.url_input_frame.pack(fill="x", padx=12, pady=12)

        url_label = ctk.CTkLabel(
            self.url_input_frame,
            text="视频链接:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        url_label.pack(anchor="w", pady=(0, 5))

        self.url_entry = ctk.CTkTextbox(
            self.url_input_frame,
            height=55,
            font=ctk.CTkFont(size=11)
        )
        self.url_entry.pack(fill="x")

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
            width=140,
            height=28
        )
        self.select_files_button.pack(side="left")

        self.clear_files_button = ctk.CTkButton(
            file_button_frame,
            text="清除",
            command=self.clear_selected_files,
            width=60,
            height=28,
            fg_color="gray",
            hover_color="dark gray"
        )
        self.clear_files_button.pack(side="left", padx=(8, 0))

        # 文件列表显示
        self.file_list_label = ctk.CTkLabel(
            self.file_input_frame,
            text="未选择文件",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.file_list_label.pack(anchor="w")

    def create_control_area(self, parent):
        """创建设置和控制区域"""
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(fill="x", pady=(0, 10))

        # 左侧：模型设置
        left_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=(12, 6), pady=12)

        # 模型选择
        model_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        model_container.pack(fill="x", pady=(0, 8))

        model_label = ctk.CTkLabel(
            model_container,
            text="AI模型:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        model_label.pack(side="left")

        self.model_var = ctk.StringVar(value=self.config.whisper_model)
        self.model_menu = ctk.CTkOptionMenu(
            model_container,
            variable=self.model_var,
            values=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
            command=self.on_model_changed,
            width=100,
            height=26
        )
        self.model_menu.pack(side="left", padx=(8, 0))

        # 模型信息
        self.model_info_label = ctk.CTkLabel(
            model_container,
            text=self.get_model_info(self.config.whisper_model),
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        self.model_info_label.pack(side="left", padx=(8, 0))

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

        # 调试模式
        debug_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        debug_frame.pack(fill="x", pady=(5, 0))

        self.debug_mode_var = ctk.BooleanVar(value=False)
        self.debug_mode_checkbox = ctk.CTkCheckBox(
            debug_frame,
            text="调试模式",
            variable=self.debug_mode_var,
            command=self.on_debug_mode_changed,
            font=ctk.CTkFont(size=11)
        )
        self.debug_mode_checkbox.pack(side="left")

        self.debug_mode_info = ctk.CTkLabel(
            debug_frame,
            text="显示后台命令执行窗口",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        self.debug_mode_info.pack(side="left", padx=(5, 0))

        # 右侧：控制按钮
        right_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=(6, 12), pady=12)

        # 开始处理按钮
        self.start_button = ctk.CTkButton(
            right_frame,
            text="开始处理",
            command=self.start_processing,
            width=90,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.start_button.pack(pady=(0, 8))

        # 清除按钮
        self.clear_button = ctk.CTkButton(
            right_frame,
            text="清除",
            command=self.clear_all,
            width=90,
            height=26,
            fg_color="gray",
            hover_color="dark gray"
        )
        self.clear_button.pack()

        # 初始化强制转录模式状态显示
        self.on_force_transcribe_changed()

    def create_status_area(self, parent):
        """创建状态和进度区域"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", pady=(0, 10))

        # 状态标签
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(fill="x", padx=12, pady=(12, 5))

        status_label = ctk.CTkLabel(
            status_container,
            text="状态:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        status_label.pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_container,
            text="就绪",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=(8, 0))

        # 进度条
        progress_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=12, pady=(0, 12))

        self.progress_bar = ctk.CTkProgressBar(progress_container)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

    def create_result_area(self, parent):
        """创建结果显示区域"""
        result_frame = ctk.CTkFrame(parent)
        result_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 结果标题和操作按钮
        result_header = ctk.CTkFrame(result_frame, fg_color="transparent")
        result_header.pack(fill="x", padx=12, pady=(12, 5))

        result_title = ctk.CTkLabel(
            result_header,
            text="处理结果:",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        result_title.pack(side="left")

        # 操作按钮组
        button_frame = ctk.CTkFrame(result_header, fg_color="transparent")
        button_frame.pack(side="right")

        self.copy_button = ctk.CTkButton(
            button_frame,
            text="复制文本",
            command=self.copy_result_text,
            width=70,
            height=24,
            state="disabled",
            font=ctk.CTkFont(size=10)
        )
        self.copy_button.pack(side="left", padx=(0, 5))

        self.open_file_button = ctk.CTkButton(
            button_frame,
            text="打开文件",
            command=self.open_result_file,
            width=70,
            height=24,
            state="disabled",
            font=ctk.CTkFont(size=10)
        )
        self.open_file_button.pack(side="left")

        # 结果文本框
        self.result_textbox = ctk.CTkTextbox(
            result_frame,
            height=120,
            font=ctk.CTkFont(size=10)
        )
        self.result_textbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def create_footer(self, parent):
        """创建底部信息"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x")

        # 版本信息
        version_label = ctk.CTkLabel(
            footer_frame,
            text="StreamScribe v1.0",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        version_label.pack(side="left")

        # 功能说明
        info_label = ctk.CTkLabel(
            footer_frame,
            text="支持 YouTube、B站 | AI转录技术",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        info_label.pack(side="right")

    # ==================== 事件处理方法 ====================

    def on_mode_changed(self):
        """处理模式改变时的回调"""
        mode = self.mode_var.get()

        if mode == "url":
            # 显示URL输入，隐藏文件选择
            self.url_input_frame.pack(fill="x", padx=12, pady=12)
            self.file_input_frame.pack_forget()
        else:
            # 显示文件选择，隐藏URL输入
            self.url_input_frame.pack_forget()
            self.file_input_frame.pack(fill="x", padx=12, pady=12)

    def on_theme_changed(self, selected_theme):
        """主题改变时的回调"""
        theme_map = {
            "🔄 自动": "auto",
            "🌞 浅色": "light",
            "🌙 深色": "dark"
        }

        theme_mode = theme_map.get(selected_theme, "auto")
        self.current_theme = theme_mode

        # 保存到配置
        self.config.set_theme_mode(theme_mode)

        # 应用主题
        self.apply_theme(theme_mode)

    def apply_theme(self, theme_mode):
        """应用指定的主题"""
        try:
            if theme_mode == "auto":
                system_theme = detect_system_theme()
                ctk.set_appearance_mode(system_theme)
                print(f"自动主题: 跟随系统 ({system_theme})")
            else:
                ctk.set_appearance_mode(theme_mode)
                print(f"手动主题: {theme_mode}")
        except Exception as e:
            print(f"应用主题失败: {e}")

    def on_model_changed(self, selected_model):
        """模型选择改变时的回调"""
        self.model_info_label.configure(text=self.get_model_info(selected_model))
        self.config.config.set('whisper', 'model', selected_model)

    def on_force_transcribe_changed(self):
        """强制转录模式改变时的回调"""
        force_mode = self.force_transcribe_var.get()

        # 只在非初始化状态时保存配置，避免初始化时覆盖带注释的配置文件
        if not getattr(self, '_initializing', False):
            self.config.set_force_transcribe_mode(force_mode)

        if force_mode:
            self.force_transcribe_info.configure(
                text="✅ 已启用：跳过字幕检测",
                text_color="#1f8b4c"
            )
        else:
            self.force_transcribe_info.configure(
                text="无视字幕，强制AI转录",
                text_color="gray"
            )

    def on_debug_mode_changed(self):
        """调试模式改变时的回调"""
        debug_mode = self.debug_mode_var.get()

        if debug_mode:
            self.show_debug_window()
            self.debug_mode_info.configure(
                text="✅ 调试窗口已打开",
                text_color="#1f8b4c"
            )
        else:
            self.hide_debug_window()
            self.debug_mode_info.configure(
                text="显示后台命令执行窗口",
                text_color="gray"
            )

    # ==================== 占位符相关方法 ====================

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
            self.url_entry.configure(text_color=("gray10", "gray90"))
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
        if self.url_entry_has_placeholder:
            self.url_entry.after(1, self._clear_url_placeholder)

    def _get_url_text(self):
        """获取URL输入框的实际文本（排除占位符）"""
        if self.url_entry_has_placeholder:
            return ""
        return self.url_entry.get("1.0", "end").strip()

    # ==================== 辅助方法 ====================

    def get_theme_display_name(self):
        """获取主题的显示名称"""
        theme_map = {
            "auto": "🔄 自动",
            "light": "🌞 浅色",
            "dark": "🌙 深色"
        }
        return theme_map.get(self.current_theme, "🔄 自动")

    def get_model_info(self, model):
        """获取模型信息"""
        model_info = {
            "tiny": "速度: 极快 | 准确度: 一般 | 显存: 极低",
            "base": "速度: 很快 | 准确度: 良好 | 显存: 低",
            "small": "速度: 快 | 准确度: 好 | 显存: 中等",
            "medium": "速度: 中等 | 准确度: 很好 | 显存: 中高",
            "large-v2": "速度: 慢 | 准确度: 极好 | 显存: 高",
            "large-v3": "速度: 慢 | 准确度: 最佳 | 显存: 高"
        }
        return model_info.get(model, "未知模型")

    def update_status(self, message):
        """更新状态显示（线程安全）"""
        def _update():
            self.status_label.configure(text=message)
            self.root.update_idletasks()

        # 如果在主线程中，直接更新；否则调度到主线程
        if threading.current_thread() == threading.main_thread():
            _update()
        else:
            self.root.after(0, _update)

    def update_progress(self, value):
        """更新进度条（线程安全）"""
        def _update():
            self.progress_bar.set(value)
            self.root.update_idletasks()

        if threading.current_thread() == threading.main_thread():
            _update()
        else:
            self.root.after(0, _update)

    def update_button_state(self, button, state):
        """更新按钮状态（线程安全）"""
        def _update():
            button.configure(state=state)
            self.root.update_idletasks()

        if threading.current_thread() == threading.main_thread():
            _update()
        else:
            self.root.after(0, _update)

    def update_textbox(self, content):
        """更新文本框内容（线程安全）"""
        def _update():
            self.result_textbox.insert("end", content)
            self.result_textbox.see("end")
            self.root.update_idletasks()

        if threading.current_thread() == threading.main_thread():
            _update()
        else:
            self.root.after(0, _update)

    # ==================== 核心功能方法 ====================

    def select_files(self):
        """选择文件"""
        # 动态生成文件类型过滤器
        audio_exts = [f"*.{fmt}" for fmt in self.config.supported_audio_formats]
        video_exts = [f"*.{fmt}" for fmt in self.config.supported_video_formats]
        all_exts = audio_exts + video_exts

        filetypes = [
            ("所有支持的文件", ";".join(all_exts)),
            ("音频文件", ";".join(audio_exts)),
            ("视频文件", ";".join(video_exts)),
            ("所有文件", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="选择音频或视频文件",
            filetypes=filetypes
        )

        if files:
            self.selected_files = list(files)
            self.update_file_list_display()

    def clear_selected_files(self):
        """清除选择的文件"""
        self.selected_files = []
        self.update_file_list_display()

    def update_file_list_display(self):
        """更新文件列表显示"""
        if not self.selected_files:
            self.file_list_label.configure(text="未选择文件")
        elif len(self.selected_files) == 1:
            filename = os.path.basename(self.selected_files[0])
            self.file_list_label.configure(text=f"已选择: {filename}")
        else:
            self.file_list_label.configure(text=f"已选择 {len(self.selected_files)} 个文件")

    def start_processing(self):
        """开始处理"""
        if self.processing:
            return

        mode = self.mode_var.get()

        if mode == "url":
            # URL模式
            url_text = self._get_url_text()
            if not url_text:
                messagebox.showwarning("警告", "请输入视频链接")
                return

            # 处理多个URL
            urls = [url.strip() for url in url_text.replace('\n', ' ').split() if url.strip()]
            if not urls:
                messagebox.showwarning("警告", "请输入有效的视频链接")
                return

            # 使用线程异步处理，避免UI卡死
            threading.Thread(target=self.process_urls, args=(urls,), daemon=True).start()

        else:
            # 文件模式
            if not self.selected_files:
                messagebox.showwarning("警告", "请选择要处理的文件")
                return

            # 使用线程异步处理，避免UI卡死
            threading.Thread(target=self.process_files, args=(self.selected_files,), daemon=True).start()

    def process_urls(self, urls):
        """处理URL列表"""
        self.processing = True
        self.update_button_state(self.start_button, "disabled")
        self.processed_results = []

        # 清空结果文本框
        def clear_textbox():
            self.result_textbox.delete("1.0", "end")
        self.root.after(0, clear_textbox)

        total_urls = len(urls)

        for i, url in enumerate(urls):
            try:
                self.update_status(f"处理第 {i+1}/{total_urls} 个视频...")
                self.update_progress((i) / total_urls)

                def status_callback(message):
                    self.update_status(f"[{i+1}/{total_urls}] {message}")

                result = self.manager.process_url(url, status_callback)

                if result['success']:
                    # 读取转录文件内容
                    transcript_file = result.get('transcript_file')
                    if transcript_file and os.path.exists(transcript_file):
                        with open(transcript_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        self.processed_results.append({
                            'title': result.get('video_title', f'视频{i+1}'),
                            'content': content,
                            'file': transcript_file
                        })

                        # 显示结果
                        self.display_result(result.get('video_title', f'视频{i+1}'), content)

                else:
                    error_msg = f"处理失败: {result.get('error', '未知错误')}"
                    self.update_textbox(f"\n=== 视频{i+1} ===\n{error_msg}\n")

            except Exception as e:
                error_msg = f"处理异常: {str(e)}"
                self.update_textbox(f"\n=== 视频{i+1} ===\n{error_msg}\n")

        self.update_progress(1.0)
        self.update_status(f"完成！处理了 {total_urls} 个视频")
        self.processing = False
        self.update_button_state(self.start_button, "normal")

        # 启用复制和打开文件按钮
        if self.processed_results:
            self.update_button_state(self.copy_button, "normal")
            if len(self.processed_results) == 1:
                self.update_button_state(self.open_file_button, "normal")
                self.current_transcript_file = self.processed_results[0]['file']

    def process_files(self, files):
        """处理文件列表"""
        self.processing = True
        self.start_button.configure(state="disabled")
        self.processed_results = []
        self.result_textbox.delete("1.0", "end")

        total_files = len(files)

        for i, file_path in enumerate(files):
            try:
                self.update_status(f"处理第 {i+1}/{total_files} 个文件...")
                self.progress_bar.set((i) / total_files)

                def status_callback(message):
                    self.update_status(f"[{i+1}/{total_files}] {message}")

                result = self.manager.process_local_file(file_path, status_callback)

                if result['success']:
                    # 读取转录文件内容
                    transcript_file = result.get('transcript_file')
                    if transcript_file and os.path.exists(transcript_file):
                        with open(transcript_file, 'r', encoding='utf-8') as f:
                            content = f.read()

                        filename = os.path.basename(file_path)
                        self.processed_results.append({
                            'title': filename,
                            'content': content,
                            'file': transcript_file
                        })

                        # 显示结果
                        self.display_result(filename, content)

                else:
                    error_msg = f"处理失败: {result.get('error', '未知错误')}"
                    filename = os.path.basename(file_path)
                    self.result_textbox.insert("end", f"\n=== {filename} ===\n{error_msg}\n")

            except Exception as e:
                error_msg = f"处理异常: {str(e)}"
                filename = os.path.basename(file_path)
                self.result_textbox.insert("end", f"\n=== {filename} ===\n{error_msg}\n")

        self.progress_bar.set(1.0)
        self.update_status(f"完成！处理了 {total_files} 个文件")
        self.processing = False
        self.start_button.configure(state="normal")

        # 启用复制和打开文件按钮
        if self.processed_results:
            self.copy_button.configure(state="normal")
            if len(self.processed_results) == 1:
                self.open_file_button.configure(state="normal")
                self.current_transcript_file = self.processed_results[0]['file']

    def display_result(self, title, content):
        """显示处理结果"""
        if len(self.processed_results) > 1:
            # 多个结果，显示标题
            self.result_textbox.insert("end", f"\n=== {title} ===\n")

        # 显示内容（截取前500字符预览）
        preview = content[:500] + "..." if len(content) > 500 else content
        self.result_textbox.insert("end", f"{preview}\n")

        # 滚动到底部
        self.result_textbox.see("end")

    def copy_result_text(self):
        """复制结果文本到剪贴板（智能复制）"""
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

            # 智能复制：单视频复制内容，多视频按标题+内容格式拼接
            if len(self.processed_results) == 1:
                # 单个结果，直接复制内容
                content = self.processed_results[0]['content']
            else:
                # 多个结果，按照 标题+内容 格式拼接
                content_parts = []
                for result in self.processed_results:
                    title = result['title']
                    text = result['content']
                    content_parts.append(f"=== {title} ===\n{text}")
                content = "\n\n".join(content_parts)

            if content:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                count = len(self.processed_results)
                self.update_status(f"已复制 {count} 个结果到剪贴板")
            else:
                self.update_status("没有可复制的内容")

        except Exception as e:
            self.update_status(f"复制失败: {str(e)}")

    def open_result_file(self):
        """打开结果文件"""
        try:
            if self.current_transcript_file and os.path.exists(self.current_transcript_file):
                os.startfile(self.current_transcript_file)
                self.update_status("已打开结果文件")
            else:
                self.update_status("没有可打开的文件")
        except Exception as e:
            self.update_status(f"打开文件失败: {str(e)}")

    def clear_all(self):
        """清除所有内容"""
        if self.processing:
            return

        # 清除URL输入框并恢复占位符
        self._set_url_placeholder()

        # 清除结果文本框
        self.result_textbox.delete("1.0", "end")

        # 清除选择的文件
        self.selected_files = []
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
        self.processed_results = []

    def show_debug_window(self):
        """显示调试窗口"""
        if self.debug_window is None:
            self.debug_window = DebugWindow(self.root)
        self.debug_window.show()

    def hide_debug_window(self):
        """隐藏调试窗口"""
        if self.debug_window:
            self.debug_window.hide()

    def log_debug_message(self, message):
        """记录调试信息"""
        if self.debug_window and self.debug_mode_var.get():
            self.debug_window.add_message(message)

    def run(self):
        """运行应用"""
        self.root.mainloop()


# 主程序入口
if __name__ == "__main__":
    app = StreamScribeCompactUI()
    app.run()
