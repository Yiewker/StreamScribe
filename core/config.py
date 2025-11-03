"""
配置模块

负责加载和提供对 config.ini 内容的访问。
"""

import configparser
import os
from pathlib import Path


class Config:
    """配置管理类"""

    def __init__(self, config_file='config.ini'):
        """
        初始化配置管理器

        Args:
            config_file (str): 配置文件路径，默认为 'config.ini'
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._tools_paths = None  # 缓存从tools_path.txt读取的路径
        self.load_config()
        self._load_tools_paths()  # 加载工具路径
    
    def load_config(self):
        """加载配置文件，如果不存在则创建默认配置"""
        if not os.path.exists(self.config_file):
            print(f"配置文件 {self.config_file} 不存在，正在创建默认配置...")
            self.create_default_config()

        self.config.read(self.config_file, encoding='utf-8')

    def _load_tools_paths(self):
        """从tools/tools_path.txt读取工具路径"""
        tools_path_file = Path('tools/tools_path.txt')
        self._tools_paths = {}

        if tools_path_file.exists():
            try:
                with open(tools_path_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 第一行：whisper-ctranslate2.exe
                    if len(lines) > 0:
                        self._tools_paths['whisper_exe'] = lines[0].strip()
                    # 第二行：yt-dlp.exe
                    if len(lines) > 1:
                        self._tools_paths['yt_dlp'] = lines[1].strip()
                    # 第三行：BBDown.exe
                    if len(lines) > 2:
                        self._tools_paths['bbdown'] = lines[2].strip()
                print(f"✅ 已从 tools_path.txt 加载工具路径")
            except Exception as e:
                print(f"⚠️ 读取 tools_path.txt 失败: {e}")
        else:
            print(f"⚠️ tools_path.txt 不存在，将使用配置文件中的路径")

    def create_default_config(self):
        """创建默认配置文件（带详细注释）"""

        # 写入配置文件（带详细注释）
        config_content = """# StreamScribe 配置文件
# 请根据您的实际环境修改以下路径设置

[general]
# 强制转录模式（跳过字幕检测，直接进行AI转录）
force_transcribe_mode = true
# 自动检测语言
auto_detect_language = true
# 启用GPU加速（需要NVIDIA GPU和CUDA环境）
enable_gpu_acceleration = false
# 最大并发任务数
max_concurrent_tasks = 2

[paths]
# yt-dlp 可执行文件路径（YouTube下载工具）
# 下载地址: https://github.com/yt-dlp/yt-dlp/releases
yt_dlp_path = ./tools/yt-dlp.exe

# BBDown 可执行文件路径（Bilibili下载工具，可选）
# 下载地址: https://github.com/nilaoda/BBDown/releases
bbdown_path = ./tools/BBDown.exe

# Whisper 虚拟环境路径
# 安装命令: pip install whisper-ctranslate2
whisper_venv_path = ./tools/whisper_env

# Whisper 脚本路径
whisper_script_path = ./tools/whisper_env/Scripts/whisper-ctranslate2.exe

# 默认输出目录
output_dir = J:/Users/ccd/Downloads

# 临时文件目录（用于存放下载的音频和字幕文件）
temp_dir = ./temp

[whisper]
# Whisper 模型设置（tiny, base, small, medium, large, large-v2, large-v3）
model = large-v3
# 输出语言（auto 为自动检测）
language = auto
# 设备类型（cpu 或 cuda）
device = cpu
# 计算类型（int8, int16, float16, float32）
compute_type = int8
# 束搜索大小
beam_size = 5
# 最佳候选数
best_of = 5
# 温度参数（0.0-1.0，越低越确定）
temperature = 0.0
# 是否基于前文进行条件生成
condition_on_previous_text = true
# 初始提示词
initial_prompt =
# 是否生成词级时间戳
word_timestamps = false
# 前置标点符号
prepend_punctuations = "\'¿([{-
# 后置标点符号
append_punctuations = "\'.,。,!?:;)}]
# 最大行宽
max_line_width = 1000
# 最大行数
max_line_count = 1
# 是否高亮显示词汇
highlight_words = false

[download]
# 最大重试次数
max_retries = 3
# 重试延迟（秒）
retry_delay = 5
# 超时时间（秒）
timeout = 300
# 代理设置（如需要）
proxy =
# 用户代理
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

[ui]
# 界面主题（system, light, dark）
theme = system
# 窗口宽度
window_width = 800
# 窗口高度
window_height = 600
# 字体大小
font_size = 12

[formats]
# 支持的视频格式
supported_video_formats = mp4,avi,mkv,mov,wmv,flv,webm,m4v,3gp,ts,mts,m2ts
# 支持的音频格式
supported_audio_formats = mp3,wav,m4a,aac,flac,ogg,wma,opus
# 首选视频质量
preferred_video_quality = best
# 首选音频质量
preferred_audio_quality = best

[advanced]
# 最大工作线程数
max_workers = 4
# 数据块大小
chunk_size = 1024
# 启用日志记录
enable_logging = true
# 日志级别（DEBUG, INFO, WARNING, ERROR）
log_level = INFO
# 自动清理临时文件
auto_cleanup = true
# 保留临时文件（调试用）
preserve_temp_files = false

"""

        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)

        print(f"✅ 默认配置文件已创建: {self.config_file}")

        # 如果是主配置文件，同时创建GPU配置示例
        if self.config_file == 'config.ini':
            self.create_gpu_config_example()

    def create_gpu_config_example(self):
        """创建GPU配置示例文件（带详细注释）"""
        gpu_config_file = 'config_gpu.ini'
        if os.path.exists(gpu_config_file):
            return  # 如果已存在则不覆盖

        # 写入GPU配置文件（带详细注释）
        gpu_config_content = """# StreamScribe GPU配置文件
# 这是GPU加速版本的配置，需要NVIDIA GPU和CUDA环境
# 如需启用GPU加速，请将此文件重命名为 config.ini

[general]
# 强制转录模式（跳过字幕检测，直接进行AI转录）
force_transcribe_mode = true
# 自动检测语言
auto_detect_language = true
# 启用GPU加速（需要NVIDIA GPU和CUDA环境）
enable_gpu_acceleration = true
# 最大并发任务数
max_concurrent_tasks = 2

[paths]
# yt-dlp 可执行文件路径（YouTube下载工具）
# 下载地址: https://github.com/yt-dlp/yt-dlp/releases
yt_dlp_path = ./tools/yt-dlp.exe

# BBDown 可执行文件路径（Bilibili下载工具，可选）
# 下载地址: https://github.com/nilaoda/BBDown/releases
bbdown_path = ./tools/BBDown.exe

# Whisper 虚拟环境路径
# 安装命令: pip install whisper-ctranslate2
whisper_venv_path = ./tools/whisper_env

# Whisper 脚本路径
whisper_script_path = ./tools/whisper_env/Scripts/whisper-ctranslate2.exe

# 默认输出目录
output_dir = J:/Users/ccd/Downloads

# 临时文件目录（用于存放下载的音频和字幕文件）
temp_dir = ./temp

[whisper]
# Whisper 模型设置（tiny, base, small, medium, large, large-v2, large-v3）
model = large-v3
# 输出语言（auto 为自动检测）
language = auto
# 设备类型（cuda 用于GPU加速）
device = cuda
# 计算类型（float16 适合GPU，比int8更快）
compute_type = float16
# 束搜索大小
beam_size = 5
# 最佳候选数
best_of = 5
# 温度参数（0.0-1.0，越低越确定）
temperature = 0.0
# 是否基于前文进行条件生成
condition_on_previous_text = true
# 初始提示词
initial_prompt =
# 是否生成词级时间戳
word_timestamps = false
# 前置标点符号
prepend_punctuations = "\'¿([{-
# 后置标点符号
append_punctuations = "\'.,。,!?:;)}]
# 最大行宽
max_line_width = 1000
# 最大行数
max_line_count = 1
# 是否高亮显示词汇
highlight_words = false

[download]
# 最大重试次数
max_retries = 3
# 重试延迟（秒）
retry_delay = 5
# 超时时间（秒）
timeout = 300
# 代理设置（如需要）
proxy =
# 用户代理
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

[ui]
# 界面主题（system, light, dark）
theme = system
# 窗口宽度
window_width = 800
# 窗口高度
window_height = 600
# 字体大小
font_size = 12

[formats]
# 支持的视频格式
supported_video_formats = mp4,avi,mkv,mov,wmv,flv,webm,m4v,3gp,ts,mts,m2ts
# 支持的音频格式
supported_audio_formats = mp3,wav,m4a,aac,flac,ogg,wma,opus
# 首选视频质量
preferred_video_quality = best
# 首选音频质量
preferred_audio_quality = best

[advanced]
# 最大工作线程数
max_workers = 4
# 数据块大小
chunk_size = 1024
# 启用日志记录
enable_logging = true
# 日志级别（DEBUG, INFO, WARNING, ERROR）
log_level = INFO
# 自动清理临时文件
auto_cleanup = true
# 保留临时文件（调试用）
preserve_temp_files = false

"""

        with open(gpu_config_file, 'w', encoding='utf-8') as f:
            f.write(gpu_config_content)

        print(f"✅ GPU配置示例已创建: {gpu_config_file}")
    
    def get(self, section, key, fallback=None):
        """
        获取配置值
        
        Args:
            section (str): 配置节名
            key (str): 配置键名
            fallback: 默认值
            
        Returns:
            str: 配置值
        """
        return self.config.get(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=False):
        """
        获取布尔类型配置值
        
        Args:
            section (str): 配置节名
            key (str): 配置键名
            fallback (bool): 默认值
            
        Returns:
            bool: 配置值
        """
        return self.config.getboolean(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=0):
        """
        获取整数类型配置值
        
        Args:
            section (str): 配置节名
            key (str): 配置键名
            fallback (int): 默认值
            
        Returns:
            int: 配置值
        """
        return self.config.getint(section, key, fallback=fallback)
    
    # 便捷方法：获取路径相关配置
    @property
    def yt_dlp_path(self):
        """获取 yt-dlp 可执行文件路径（优先从tools_path.txt读取）"""
        if self._tools_paths and 'yt_dlp' in self._tools_paths:
            return self._tools_paths['yt_dlp']
        return self.get('paths', 'yt_dlp_path')

    @property
    def bbdown_path(self):
        """获取 BBDown 可执行文件路径（优先从tools_path.txt读取）"""
        if self._tools_paths and 'bbdown' in self._tools_paths:
            return self._tools_paths['bbdown']
        return self.get('paths', 'bbdown_path')

    @property
    def whisper_venv_path(self):
        """获取 Whisper 虚拟环境路径"""
        # 如果从tools_path.txt读取到了whisper_exe，提取其目录作为venv路径
        if self._tools_paths and 'whisper_exe' in self._tools_paths:
            whisper_exe = self._tools_paths['whisper_exe']
            # 从路径中提取venv路径（去掉Scripts\whisper-ctranslate2.exe部分）
            venv_path = str(Path(whisper_exe).parent.parent)
            return venv_path
        return self.get('paths', 'whisper_venv_path')
    
    @property
    def output_dir(self):
        """获取输出目录"""
        path = self.get('paths', 'output_dir')
        # 确保目录存在
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def temp_dir(self):
        """获取临时文件目录"""
        path = self.get('paths', 'temp_dir')
        # 确保目录存在
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    
    # 便捷方法：获取网络相关配置
    @property
    def proxy(self):
        """获取代理设置"""
        return self.get('network', 'proxy')
    
    # 便捷方法：获取 Whisper 相关配置
    @property
    def whisper_model(self):
        """获取 Whisper 模型"""
        return self.get('whisper', 'model', 'base')
    
    @property
    def whisper_language(self):
        """获取 Whisper 语言设置"""
        return self.get('whisper', 'language', 'auto')

    @property
    def whisper_output_format(self):
        """获取 Whisper 输出格式"""
        return self.get('whisper', 'output_format', 'txt')

    @property
    def whisper_initial_prompt(self):
        """获取 Whisper 初始提示词"""
        return self.get('whisper', 'initial_prompt', '以下是普通话的简体中文。')

    @property
    def whisper_output_format_srt(self):
        """获取是否输出SRT格式（默认为True）"""
        return self.getboolean('whisper', 'output_format_srt', True)

    @property
    def whisper_compute_type(self):
        """获取量化类型"""
        return self.get('whisper', 'compute_type', 'int8')

    @property
    def whisper_vad_filter(self):
        """获取是否启用 VAD 语音活动检测"""
        return self.getboolean('whisper', 'vad_filter', True)

    @property
    def whisper_device(self):
        """获取设备类型"""
        return self.get('whisper', 'device', 'cpu')

    @property
    def whisper_device_index(self):
        """获取 GPU 设备索引"""
        return self.getint('whisper', 'device_index', 0)

    def get_compute_type_for_model(self, model):
        """
        根据模型自动获取最佳量化类型

        Args:
            model (str): 模型名称

        Returns:
            str: 对应的量化类型
        """
        # 模型和量化类型映射
        model_compute_map = {
            'base': 'int8',
            'small': 'int8_float16',
            'medium': 'float16',
            'large-v2': 'float16',
            'large-v3': 'float16',
            'large-v3-turbo': 'int8_float16',  # 新增：速度优秀
            'belle-whisper-v3-zh-punct': 'int8_float16'  # 新增：质量优秀
        }

        return model_compute_map.get(model, 'int8')

    def get_model_directory(self, model):
        """
        获取自定义模型的目录路径（仅用于belle模型）

        Args:
            model (str): 模型名称

        Returns:
            str: 模型目录路径，如果不是自定义模型则返回None
        """
        if model == 'belle-whisper-v3-zh-punct':
            return r'J:\Users\ccd\Desktop\projects\asr\Belle-whisper-large-models\Belle-whisper-v3-zh-punct-ct2'
        return None

    def get_available_models(self):
        """
        获取可用的模型列表

        Returns:
            list: 可用的模型列表
        """
        return ['base', 'small', 'medium', 'large-v2', 'large-v3', 'large-v3-turbo', 'belle-whisper-v3-zh-punct']

    @property
    def supported_audio_formats(self):
        """获取支持的音频格式列表"""
        formats_str = self.get('local_files', 'supported_audio_formats', 'mp3,wav,m4a,aac,flac')
        return [fmt.strip().lower() for fmt in formats_str.split(',')]

    @property
    def supported_video_formats(self):
        """获取支持的视频格式列表"""
        formats_str = self.get('local_files', 'supported_video_formats', 'mp4,avi,mkv,mov,wmv')
        return [fmt.strip().lower() for fmt in formats_str.split(',')]

    @property
    def max_batch_files(self):
        """获取批量处理的最大文件数量"""
        return self.getint('local_files', 'max_batch_files', 20)

    def get_all_supported_formats(self):
        """获取所有支持的文件格式"""
        return self.supported_audio_formats + self.supported_video_formats

    # BBDown 相关配置
    @property
    def bbdown_quality(self):
        """获取 BBDown 下载质量"""
        return self.get('bbdown', 'quality', 'highest')

    @property
    def bbdown_download_subtitle(self):
        """获取是否下载字幕"""
        return self.getboolean('bbdown', 'download_subtitle', True)

    @property
    def bbdown_download_danmaku(self):
        """获取是否下载弹幕"""
        return self.getboolean('bbdown', 'download_danmaku', False)

    @property
    def bbdown_audio_format(self):
        """获取 BBDown 音频格式"""
        return self.get('bbdown', 'audio_format', 'mp3')

    # 主题相关配置
    @property
    def theme_mode(self):
        """获取主题模式"""
        return self.get('theme', 'mode', 'auto')

    @property
    def show_theme_switch(self):
        """获取是否显示主题切换按钮"""
        return self.getboolean('theme', 'show_theme_switch', True)

    def set_theme_mode(self, mode):
        """设置主题模式"""
        if mode in ['auto', 'light', 'dark']:
            self.config.set('theme', 'mode', mode)
            self.save()
        else:
            raise ValueError(f"无效的主题模式: {mode}")

    def set_force_transcribe_mode(self, enabled):
        """设置强制转录模式"""
        self.config.set('general', 'force_transcribe_mode', str(enabled).lower())
        self.save()

    def set_output_format_srt(self, enabled):
        """设置是否输出SRT格式"""
        if not self.config.has_section('whisper'):
            self.config.add_section('whisper')
        self.config.set('whisper', 'output_format_srt', str(enabled).lower())
        self.save()

    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    # 便捷方法：获取应用程序相关配置
    @property
    def app_title(self):
        """获取应用程序标题"""
        return self.get('general', 'app_title', 'StreamScribe')
    
    @property
    def window_width(self):
        """获取窗口宽度"""
        return self.getint('general', 'window_width', 800)
    
    @property
    def window_height(self):
        """获取窗口高度"""
        return self.getint('general', 'window_height', 600)
    
    @property
    def auto_open_result(self):
        """获取是否自动打开结果文件"""
        return self.getboolean('general', 'auto_open_result', True)

    @property
    def force_transcribe_mode(self):
        """获取是否启用强制转录模式"""
        return self.getboolean('general', 'force_transcribe_mode', False)


# 全局配置实例
_config_instance = None

def get_config():
    """
    获取全局配置实例
    
    Returns:
        Config: 配置实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
