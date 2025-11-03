"""
AI转录模块

封装了对 whisper-ctranslate2 的调用，负责将音频文件转换为文稿。
"""

import os
import subprocess
import logging
import time
import re
import json
from pathlib import Path
from .config import get_config


class WhisperTranscriber:
    """Whisper 转录器类"""
    
    def __init__(self):
        """初始化转录器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.debug_callback = None

    def set_debug_callback(self, callback):
        """设置调试回调函数"""
        self.debug_callback = callback

    def _debug_log(self, message):
        """调试日志"""
        if self.debug_callback:
            self.debug_callback(message)

    def _get_audio_duration(self, audio_path):
        """
        获取音频文件时长（秒）

        Args:
            audio_path (str): 音频文件路径

        Returns:
            float: 音频时长（秒），如果获取失败返回0
        """
        ffprobe_commands = [
            'ffprobe',  # 系统 PATH 中的 ffprobe
            'J:\\app\\ffmpeg\\bin\\ffprobe.exe',  # 常见的 ffprobe 位置
        ]

        for ffprobe_cmd in ffprobe_commands:
            try:
                command = [
                    ffprobe_cmd,
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'json',
                    audio_path
                ]

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    duration = float(data.get('format', {}).get('duration', 0))
                    self.logger.info(f"音频时长: {duration:.2f}秒")
                    return duration

            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
                continue

        self.logger.warning("无法获取音频时长，将使用0作为默认值")
        return 0.0

    def run_whisper(self, audio_path, output_dir=None):
        """
        使用 Whisper 转录音频文件

        Args:
            audio_path (str): 音频文件路径
            output_dir (str): 输出目录，默认使用配置中的输出目录

        Returns:
            dict: 包含以下键的字典:
                - transcript_file (str): 生成的文稿文件路径
                - audio_duration (float): 音频时长（秒）
                - processing_time (float): 处理时间（秒）
                - speed_ratio (float): 加速倍率（音频时长/处理时间）

        Raises:
            FileNotFoundError: 当音频文件或 Whisper 环境不存在时
            subprocess.CalledProcessError: 当 Whisper 执行失败时
            Exception: 其他错误
        """
        # 验证输入文件
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        # 设置输出目录
        if output_dir is None:
            output_dir = self.config.output_dir

        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 获取音频时长
        audio_duration = self._get_audio_duration(audio_path)

        # 记录开始时间
        start_time = time.time()

        # 使用 whisper-ctranslate2 进行转录
        try:
            command = self._build_whisper_command(audio_path, output_dir)
            self.logger.info(f"执行 whisper-ctranslate2 命令: {' '.join(command)}")

            # 打印完整命令供用户复制测试
            command_str = ' '.join(command)
            print(f"\n🔍 执行 whisper-ctranslate2 转录:")
            print(f"📋 {command_str}")
            print()

            # 发送到调试窗口
            self._debug_log(f"🔍 执行 whisper-ctranslate2 转录:")
            self._debug_log(f"📋 {command_str}")

            # 设置环境变量解决编码问题
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'

            # 执行命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=False,  # 使用字节模式避免编码问题
                timeout=3600,  # 1小时超时
                env=env
            )

            # 解码输出信息（无论成功还是失败都要看）
            stdout_msg = ""
            stderr_msg = ""

            try:
                stdout_msg = result.stdout.decode('utf-8', errors='ignore')
            except:
                try:
                    stdout_msg = result.stdout.decode('gbk', errors='ignore')
                except:
                    stdout_msg = str(result.stdout)

            try:
                stderr_msg = result.stderr.decode('utf-8', errors='ignore')
            except:
                try:
                    stderr_msg = result.stderr.decode('gbk', errors='ignore')
                except:
                    stderr_msg = str(result.stderr)

            # 记录whisper的输出
            if stdout_msg.strip():
                self.logger.info(f"whisper stdout: {stdout_msg.strip()}")
            if stderr_msg.strip():
                self.logger.info(f"whisper stderr: {stderr_msg.strip()}")

            if result.returncode != 0:
                self.logger.error(f"whisper-ctranslate2 执行失败，返回码: {result.returncode}")
                self.logger.error(f"错误信息: {stderr_msg}")
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)

            # 从whisper输出中解析生成的文件名
            self.logger.info("whisper-ctranslate2 执行完成，开始查找生成的文稿文件")

            transcript_file = self._parse_transcript_file_from_output(stdout_msg, stderr_msg, audio_path, output_dir)

            if not transcript_file or not os.path.exists(transcript_file):
                self.logger.error("未找到生成的文稿文件")
                self.logger.error(f"预期的音频文件名: {Path(audio_path).stem}")
                self.logger.error(f"输出目录: {output_dir}")
                raise Exception("未找到生成的文稿文件")

            # 计算处理时间和加速倍率
            end_time = time.time()
            processing_time = end_time - start_time
            speed_ratio = audio_duration / processing_time if processing_time > 0 and audio_duration > 0 else 0

            self.logger.info(f"转录完成，文稿文件: {transcript_file}")
            self.logger.info(f"⏱️  处理时间: {processing_time:.2f}秒")
            self.logger.info(f"🎵 音频时长: {audio_duration:.2f}秒")
            self.logger.info(f"⚡ 加速倍率: {speed_ratio:.2f}x")

            # 打印到控制台
            print(f"\n✅ 转录完成！")
            print(f"⏱️  处理时间: {processing_time:.2f}秒")
            print(f"🎵 音频时长: {audio_duration:.2f}秒")
            print(f"⚡ 加速倍率: {speed_ratio:.2f}x\n")

            return {
                'transcript_file': transcript_file,
                'audio_duration': audio_duration,
                'processing_time': processing_time,
                'speed_ratio': speed_ratio
            }

        except subprocess.TimeoutExpired:
            raise Exception("Whisper 执行超时")
        except Exception as e:
            self.logger.error(f"转录过程中出错: {str(e)}")
            raise
    
    def _build_whisper_command(self, audio_path, output_dir):
        """
        构建 whisper-ctranslate2 命令

        Args:
            audio_path (str): 音频文件路径
            output_dir (str): 输出目录

        Returns:
            list: 命令参数列表
        """
        # 获取whisper-ctranslate2可执行文件路径（优先从tools_path.txt读取）
        if hasattr(self.config, '_tools_paths') and self.config._tools_paths and 'whisper_exe' in self.config._tools_paths:
            whisper_exe = self.config._tools_paths['whisper_exe']
        else:
            venv_path = self.config.whisper_venv_path
            whisper_exe = os.path.join(venv_path, 'Scripts', 'whisper-ctranslate2.exe')

        # 验证可执行文件存在
        if not os.path.exists(whisper_exe):
            raise FileNotFoundError(f"whisper-ctranslate2 可执行文件不存在: {whisper_exe}")

        # 获取当前模型
        current_model = self.config.whisper_model

        # 检查是否是自定义模型（需要使用model_directory参数）
        model_directory = self.config.get_model_directory(current_model)

        # 构建基础命令
        command = [whisper_exe, audio_path]

        # 如果是自定义模型，使用model_directory参数
        if model_directory:
            command.extend(['--model_directory', model_directory])
        else:
            command.extend(['--model', current_model])

        # 根据配置决定输出格式
        if self.config.whisper_output_format_srt:
            command.extend(['--output_format', 'srt'])
        else:
            command.extend(['--output_format', 'txt'])

        command.extend(['--output_dir', output_dir])

        # 量化优化（根据模型自动选择最佳量化类型）
        compute_type = self.config.get_compute_type_for_model(current_model)
        command.extend(['--compute_type', compute_type])

        # VAD 语音活动检测 - 跳过静音部分
        if self.config.whisper_vad_filter:
            command.extend(['--vad_filter', 'True'])

        # 设备选择（CPU 或 GPU）
        if self.config.whisper_device != 'cpu':
            command.extend(['--device', self.config.whisper_device])
            if self.config.whisper_device == 'cuda':
                command.extend(['--device_index', str(self.config.whisper_device_index)])

        # 添加语言设置（如果不是自动检测）
        if self.config.whisper_language != 'auto':
            # 将语言代码转换为 whisper-ctranslate2 支持的格式
            language_map = {
                'zh': 'zh',
                'zh-Hans': 'zh',
                'zh-Hant': 'zh',
                'en': 'en',
                'auto': None
            }
            language = language_map.get(self.config.whisper_language, self.config.whisper_language)
            if language:
                command.extend(['--language', language])

        # 添加初始提示词（提高中文识别准确度）
        if self.config.whisper_initial_prompt:
            command.extend(['--initial_prompt', self.config.whisper_initial_prompt])

        return command

    def _parse_transcript_file_from_output(self, stdout_msg, stderr_msg, audio_path, output_dir):
        """
        从whisper-ctranslate2的输出中解析生成的文件名

        Args:
            stdout_msg (str): 标准输出
            stderr_msg (str): 标准错误输出
            audio_path (str): 音频文件路径
            output_dir (str): 输出目录

        Returns:
            str: 文稿文件路径，如果未找到则返回 None
        """
        # whisper-ctranslate2 通常会在输出中显示保存的文件路径
        # 例如: "Saving output to /path/to/file.srt"
        # 或者: "Writing to /path/to/file.txt"

        combined_output = stdout_msg + "\n" + stderr_msg

        # 尝试从输出中提取文件路径
        # 常见模式：
        # - "Saving output to <path>"
        # - "Writing to <path>"
        # - "Output written to <path>"
        patterns = [
            r'Saving output to\s+(.+)',
            r'Writing to\s+(.+)',
            r'Output written to\s+(.+)',
            r'Saved to\s+(.+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, combined_output, re.IGNORECASE)
            if matches:
                # 取最后一个匹配（最新的输出）
                file_path = matches[-1].strip()
                # 移除可能的引号
                file_path = file_path.strip('"\'')

                if os.path.exists(file_path):
                    self.logger.info(f"从whisper输出中解析到文件: {file_path}")
                    return file_path

        # 如果从输出中解析失败，使用原来的查找方法
        self.logger.info("无法从whisper输出中解析文件路径，使用文件名匹配方法")
        return self._find_transcript_file(audio_path, output_dir)

    def _find_transcript_file(self, audio_path, output_dir):
        """
        查找生成的文稿文件（基于文件名匹配）

        Args:
            audio_path (str): 原始音频文件路径
            output_dir (str): 输出目录

        Returns:
            str: 文稿文件路径，如果未找到则返回 None
        """
        # 获取音频文件的基础名称（不含扩展名）
        audio_name = Path(audio_path).stem

        # 根据配置确定输出格式
        if self.config.whisper_output_format_srt:
            possible_extensions = ['.srt', '.txt', '.vtt', '.json']
        else:
            possible_extensions = ['.txt', '.srt', '.vtt', '.json']

        self.logger.info(f"查找转录文件，音频文件名: {audio_name}")

        # 方法1：精确匹配
        for ext in possible_extensions:
            transcript_file = os.path.join(output_dir, f"{audio_name}{ext}")

            if os.path.exists(transcript_file):
                self.logger.info(f"找到转录文件: {transcript_file}")
                return transcript_file
            else:
                # 尝试使用Path对象检查
                try:
                    path_obj = Path(transcript_file)
                    if path_obj.exists():
                        return str(path_obj)
                except Exception:
                    pass

        # 方法1.5：尝试不同的文件名变体（whisper可能会修改文件名）
        # whisper有时会截断长文件名或替换特殊字符
        audio_name_variants = [
            audio_name,
            audio_name.replace('_', ' '),  # 下划线替换为空格
            audio_name.replace(' ', '_'),  # 空格替换为下划线
        ]

        # 如果文件名太长，尝试截断版本
        if len(audio_name) > 100:
            audio_name_variants.extend([
                audio_name[:100],
                audio_name[:80],
                audio_name[:60]
            ])

        for variant in audio_name_variants:
            if variant != audio_name:  # 避免重复检查
                for ext in possible_extensions:
                    transcript_file = os.path.join(output_dir, f"{variant}{ext}")
                    if os.path.exists(transcript_file):
                        self.logger.info(f"找到变体转录文件: {transcript_file}")
                        return transcript_file

        # 方法2：查找最新的文本文件（仅限最近5分钟内生成的文件）
        output_path = Path(output_dir)
        current_time = time.time()
        recent_files = []

        for ext in possible_extensions:
            for file_path in output_path.glob(f"*{ext}"):
                file_mtime = file_path.stat().st_mtime
                # 只考虑最近5分钟内修改的文件
                if current_time - file_mtime < 300:  # 300秒 = 5分钟
                    recent_files.append(file_path)

        if recent_files:
            # 按修改时间排序，取最新的
            latest_file = max(recent_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"找到最近生成的文件: {latest_file}")
            return str(latest_file)

        # 如果还是找不到，记录错误
        self.logger.error(f"未找到转录文件，输出目录内容:")
        try:
            for file_path in output_path.iterdir():
                self.logger.error(f"  - {file_path.name}")
        except Exception as e:
            self.logger.error(f"无法列出目录内容: {e}")

        return None
    
    def get_supported_formats(self):
        """
        获取支持的音频格式
        
        Returns:
            list: 支持的音频格式列表
        """
        return [
            '.mp3', '.wav', '.flac', '.m4a', '.aac', 
            '.ogg', '.wma', '.mp4', '.avi', '.mkv'
        ]
    
    def validate_audio_file(self, audio_path):
        """
        验证音频文件是否支持
        
        Args:
            audio_path (str): 音频文件路径
            
        Returns:
            bool: 是否支持该音频文件
        """
        if not os.path.exists(audio_path):
            return False
        
        file_ext = Path(audio_path).suffix.lower()
        return file_ext in self.get_supported_formats()


# 便捷函数
def transcribe_audio(audio_path, output_dir=None):
    """
    转录音频文件的便捷函数

    Args:
        audio_path (str): 音频文件路径
        output_dir (str): 输出目录

    Returns:
        dict: 包含transcript_file, audio_duration, processing_time, speed_ratio的字典
    """
    transcriber = WhisperTranscriber()
    return transcriber.run_whisper(audio_path, output_dir)
