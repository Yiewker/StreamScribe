"""
本地文件处理器

处理本地音频和视频文件的转录。
"""

import os
import subprocess
import logging
from pathlib import Path
from ..config import get_config
from ..transcriber import WhisperTranscriber
from ..utils import sanitize_filename


class LocalFileHandler:
    """本地文件处理器类"""
    
    def __init__(self):
        """初始化本地文件处理器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.transcriber = WhisperTranscriber()
    
    def get_transcript(self, file_path, status_callback=None):
        """
        获取本地文件的文稿
        
        Args:
            file_path (str): 本地文件路径
            status_callback (callable): 状态回调函数
            
        Returns:
            dict: 处理结果
        """
        result = {
            'success': False,
            'transcript_file': None,
            'error': None,
            'file_name': None,
            'method': 'whisper'  # 本地文件总是使用 whisper 转录
        }
        
        try:
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            file_path = os.path.abspath(file_path)
            file_name = Path(file_path).name
            result['file_name'] = file_name
            
            # 更新状态
            if status_callback:
                status_callback(f"开始处理文件: {file_name}")
            
            # 验证文件格式
            if not self._is_supported_format(file_path):
                supported_formats = ', '.join(self.config.get_all_supported_formats())
                raise ValueError(f"不支持的文件格式。支持的格式: {supported_formats}")
            
            # 检查是否需要提取音频
            if self._is_video_file(file_path):
                if status_callback:
                    status_callback("检测到视频文件，正在提取音频...")
                
                audio_file = self._extract_audio_from_video(file_path)
            else:
                if status_callback:
                    status_callback("检测到音频文件，准备转录...")
                
                audio_file = file_path
            
            # 使用 Whisper 转录
            if status_callback:
                status_callback("正在使用 AI 转录音频...")

            transcribe_result = self.transcriber.run_whisper(audio_file, self.config.output_dir)
            transcript_file = transcribe_result['transcript_file']

            # 记录处理信息
            self.logger.info(f"处理时间: {transcribe_result['processing_time']:.2f}秒, 加速倍率: {transcribe_result['speed_ratio']:.2f}x")

            # 如果提取了临时音频文件，清理它
            if audio_file != file_path:
                try:
                    os.remove(audio_file)
                except:
                    pass

            result['transcript_file'] = transcript_file
            result['processing_time'] = transcribe_result['processing_time']
            result['audio_duration'] = transcribe_result['audio_duration']
            result['speed_ratio'] = transcribe_result['speed_ratio']
            result['success'] = True
            
            if status_callback:
                status_callback("文稿生成完成！")
            
            self.logger.info(f"成功处理本地文件: {file_path}")
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            self.logger.error(f"处理本地文件失败: {error_msg}")
            
            if status_callback:
                status_callback(f"处理失败: {error_msg}")
        
        return result
    
    def _is_supported_format(self, file_path):
        """检查文件格式是否支持"""
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        supported_formats = self.config.get_all_supported_formats()
        return file_ext in supported_formats
    
    def _is_video_file(self, file_path):
        """检查是否为视频文件"""
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        return file_ext in self.config.supported_video_formats
    
    def _extract_audio_from_video(self, video_path):
        """从视频文件中提取音频"""
        video_name = Path(video_path).stem
        safe_name = sanitize_filename(video_name)
        audio_file = os.path.join(self.config.temp_dir, f"{safe_name}_extracted.mp3")
        
        # 使用 ffmpeg 提取音频（如果可用）
        # 首先尝试使用系统的 ffmpeg
        ffmpeg_commands = [
            'ffmpeg',  # 系统 PATH 中的 ffmpeg
            'J:\\app\\ffmpeg\\bin\\ffmpeg.exe',  # 常见的 ffmpeg 位置
        ]
        
        for ffmpeg_cmd in ffmpeg_commands:
            try:
                command = [
                    ffmpeg_cmd,
                    '-i', video_path,
                    '-vn',  # 不包含视频
                    '-acodec', 'mp3',
                    '-ab', '192k',
                    '-ar', '44100',
                    '-y',  # 覆盖输出文件
                    audio_file
                ]
                
                print(f"\n🔍 执行 ffmpeg 音频提取:")
                print(f"📋 {' '.join(command)}")
                print()
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=False,
                    timeout=1800  # 30分钟超时
                )
                
                if result.returncode == 0 and os.path.exists(audio_file):
                    self.logger.info(f"成功提取音频: {audio_file}")
                    return audio_file
                
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue
        
        # 如果 ffmpeg 不可用，尝试直接使用视频文件
        # Whisper 可能能够直接处理某些视频格式
        self.logger.warning("ffmpeg 不可用，尝试直接处理视频文件")
        return video_path
    
    def get_supported_formats_display(self):
        """获取支持格式的显示字符串"""
        audio_formats = ', '.join(self.config.supported_audio_formats)
        video_formats = ', '.join(self.config.supported_video_formats)
        return f"音频: {audio_formats}\n视频: {video_formats}"


# 便捷函数
def process_local_file(file_path, status_callback=None):
    """
    处理本地文件的便捷函数
    
    Args:
        file_path (str): 本地文件路径
        status_callback (callable): 状态回调函数
        
    Returns:
        dict: 处理结果
    """
    handler = LocalFileHandler()
    return handler.get_transcript(file_path, status_callback)
