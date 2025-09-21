"""
工具函数模块

存放通用辅助函数，例如 VTT 字幕文件解析器等。
"""

import re
import os
import logging
from pathlib import Path
from datetime import datetime


def setup_logging():
    """设置日志记录"""
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    try:
        file_handler = logging.FileHandler('streamscribe.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"警告: 无法创建日志文件: {e}")

    return logging.getLogger(__name__)


def parse_vtt(vtt_file_path):
    """
    解析 VTT 字幕文件，提取纯文本内容
    
    Args:
        vtt_file_path (str): VTT 文件路径
        
    Returns:
        str: 提取的纯文本内容
        
    Raises:
        FileNotFoundError: 当文件不存在时
        Exception: 当解析失败时
    """
    if not os.path.exists(vtt_file_path):
        raise FileNotFoundError(f"VTT 文件不存在: {vtt_file_path}")
    
    try:
        with open(vtt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 移除 WEBVTT 头部
        content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.MULTILINE | re.DOTALL)
        
        # 移除时间戳行 (格式: 00:00:00.000 --> 00:00:00.000)
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', content)
        
        # 移除字幕序号行
        content = re.sub(r'^\d+\n', '', content, flags=re.MULTILINE)
        
        # 移除 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除多余的空行，保留段落结构
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        return '\n'.join(lines)
        
    except Exception as e:
        raise Exception(f"解析 VTT 文件失败: {str(e)}")


def sanitize_filename(filename):
    """
    清理文件名，移除不合法字符

    Args:
        filename (str): 原始文件名

    Returns:
        str: 清理后的文件名
    """
    # 移除或替换不合法字符（包括更多特殊字符）
    # Windows文件名非法字符 + 中文标点 + 其他特殊字符
    illegal_chars = r'[<>:"/\\|?*;，。！？、【】（）《》""''`~@#$%^&+={}[\]；]'
    filename = re.sub(illegal_chars, '_', filename)

    # 移除连续的下划线
    filename = re.sub(r'_+', '_', filename)

    # 移除多余的空格和点
    filename = re.sub(r'\s+', ' ', filename).strip()
    filename = filename.strip('._')

    # 如果文件名为空或只有下划线，使用默认名称
    if not filename or filename.replace('_', '').strip() == '':
        filename = 'video'

    # 限制文件名长度
    if len(filename) > 150:  # 减少长度限制，避免路径过长
        filename = filename[:150].rstrip('_')

    return filename


def generate_output_filename(video_title, platform='unknown'):
    """
    生成输出文件名
    
    Args:
        video_title (str): 视频标题
        platform (str): 平台名称
        
    Returns:
        str: 生成的文件名（不包含扩展名）
    """
    # 清理标题
    clean_title = sanitize_filename(video_title)
    
    # 添加时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 组合文件名
    filename = f"{platform}_{clean_title}_{timestamp}"
    
    return filename


def extract_video_id_from_url(url):
    """
    从 URL 中提取视频 ID
    
    Args:
        url (str): 视频 URL
        
    Returns:
        tuple: (platform, video_id) 或 (None, None) 如果无法识别
    """
    # YouTube URL 模式
    youtube_patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            return 'youtube', match.group(1)

    # Bilibili URL 模式
    bilibili_patterns = [
        r'bilibili\.com/video/(BV[a-zA-Z0-9]+)',
        r'bilibili\.com/video/(av\d+)',
        r'b23\.tv/([a-zA-Z0-9]+)',
        r'bilibili\.com/s/video/(BV[a-zA-Z0-9]+)'
    ]

    for pattern in bilibili_patterns:
        match = re.search(pattern, url)
        if match:
            return 'bilibili', match.group(1)

    return None, None


def format_duration(seconds):
    """
    格式化时长显示
    
    Args:
        seconds (int): 秒数
        
    Returns:
        str: 格式化的时长字符串
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def ensure_directory_exists(directory_path):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path (str): 目录路径
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def clean_temp_files(temp_dir, max_age_hours=24):
    """
    清理临时文件
    
    Args:
        temp_dir (str): 临时文件目录
        max_age_hours (int): 文件最大保留时间（小时）
    """
    try:
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return
        
        current_time = datetime.now()
        
        for file_path in temp_path.iterdir():
            if file_path.is_file():
                file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    file_path.unlink()
                    logging.info(f"已删除过期临时文件: {file_path}")
                    
    except Exception as e:
        logging.warning(f"清理临时文件时出错: {str(e)}")


def validate_url(url):
    """
    验证 URL 格式
    
    Args:
        url (str): 要验证的 URL
        
    Returns:
        bool: URL 是否有效
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP 地址
        r'(?::\d+)?'  # 可选端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None
