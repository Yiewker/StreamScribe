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
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在")
        
        self.config.read(self.config_file, encoding='utf-8')
    
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
        """获取 yt-dlp 可执行文件路径"""
        return self.get('paths', 'yt_dlp_path')

    @property
    def bbdown_path(self):
        """获取 BBDown 可执行文件路径"""
        return self.get('paths', 'bbdown_path')

    @property
    def whisper_venv_path(self):
        """获取 Whisper 虚拟环境路径"""
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
    def whisper_batched(self):
        """获取是否启用批处理推理"""
        return self.getboolean('whisper', 'batched', True)

    @property
    def whisper_batch_size(self):
        """获取批处理大小"""
        return self.getint('whisper', 'batch_size', 32)

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
            'large-v3': 'float16'
        }

        return model_compute_map.get(model, 'int8')

    def get_available_models(self):
        """
        获取可用的模型列表

        Returns:
            list: 可用的模型列表
        """
        return ['base', 'small', 'medium', 'large-v2', 'large-v3']

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
