"""
AI转录模块

封装了对 whisper-ctranslate2 的调用，负责将音频文件转换为文稿。
"""

import os
import subprocess
import logging
from pathlib import Path
from .config import get_config


class WhisperTranscriber:
    """Whisper 转录器类"""
    
    def __init__(self):
        """初始化转录器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
    
    def run_whisper(self, audio_path, output_dir=None):
        """
        使用 Whisper 转录音频文件
        
        Args:
            audio_path (str): 音频文件路径
            output_dir (str): 输出目录，默认使用配置中的输出目录
            
        Returns:
            str: 生成的文稿文件路径
            
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
        
        # 使用 whisper-ctranslate2 进行转录
        try:
            command = self._build_whisper_command(audio_path, output_dir)
            self.logger.info(f"执行 whisper-ctranslate2 命令: {' '.join(command)}")

            # 打印完整命令供用户复制测试
            print(f"\n🔍 执行 whisper-ctranslate2 转录:")
            print(f"📋 {' '.join(command)}")
            print()

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

            # 查找生成的文稿文件
            self.logger.info("whisper-ctranslate2 执行完成，开始查找生成的文稿文件")

            # 先列出输出目录中的所有文件，帮助调试
            self.logger.info(f"whisper执行后，输出目录 {output_dir} 中的文件:")
            try:
                output_path = Path(output_dir)
                for file_path in sorted(output_path.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True):
                    if file_path.is_file():
                        import time
                        mtime = time.ctime(file_path.stat().st_mtime)
                        size = file_path.stat().st_size
                        self.logger.info(f"  - {file_path.name} (大小: {size} 字节, 修改时间: {mtime})")
            except Exception as e:
                self.logger.error(f"无法列出目录内容: {e}")

            transcript_file = self._find_transcript_file(audio_path, output_dir)

            if not transcript_file or not os.path.exists(transcript_file):
                self.logger.error("未找到生成的文稿文件")
                self.logger.error(f"预期的音频文件名: {Path(audio_path).stem}")
                self.logger.error(f"输出目录: {output_dir}")
                raise Exception("未找到生成的文稿文件")

            self.logger.info(f"转录完成，文稿文件: {transcript_file}")
            return transcript_file
            
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
        # 获取虚拟环境中的 whisper-ctranslate2 可执行文件
        venv_path = self.config.whisper_venv_path
        whisper_exe = os.path.join(venv_path, 'Scripts', 'whisper-ctranslate2.exe')

        # 验证可执行文件存在
        if not os.path.exists(whisper_exe):
            raise FileNotFoundError(f"whisper-ctranslate2 可执行文件不存在: {whisper_exe}")

        # 构建基础命令
        command = [
            whisper_exe,
            audio_path,
            '--model', self.config.whisper_model,
            '--output_format', self.config.whisper_output_format,
            '--output_dir', output_dir
        ]

        # 性能优化选项（从配置文件读取）
        # 1. 批处理推理 - 2x-4x 速度提升
        if self.config.whisper_batched:
            command.extend(['--batched', 'True'])
            command.extend(['--batch_size', str(self.config.whisper_batch_size)])

        # 2. 量化优化（根据模型自动选择最佳量化类型）
        compute_type = self.config.get_compute_type_for_model(self.config.whisper_model)
        command.extend(['--compute_type', compute_type])

        # 3. VAD 语音活动检测 - 跳过静音部分
        if self.config.whisper_vad_filter:
            command.extend(['--vad_filter', 'True'])

        # 4. 设备选择（CPU 或 GPU）
        if self.config.whisper_device != 'cpu':
            command.extend(['--device', self.config.whisper_device])
            if self.config.whisper_device == 'cuda':
                command.extend(['--device_index', str(self.config.whisper_device_index)])

        # 添加语言设置（如果不是自动检测）
        if self.config.whisper_language != 'auto':
            # 将语言代码转换为 whisper-ctranslate2 支持的格式
            language_map = {
                'zh': 'Chinese',
                'zh-Hans': 'Chinese',
                'zh-Hant': 'Chinese',
                'en': 'English',
                'auto': None
            }
            language = language_map.get(self.config.whisper_language, self.config.whisper_language)
            if language:
                command.extend(['--language', language])

        # 添加初始提示词（提高中文识别准确度）
        if self.config.whisper_initial_prompt:
            command.extend(['--initial_prompt', self.config.whisper_initial_prompt])

        return command
    
    def _find_transcript_file(self, audio_path, output_dir):
        """
        查找生成的文稿文件

        Args:
            audio_path (str): 原始音频文件路径
            output_dir (str): 输出目录

        Returns:
            str: 文稿文件路径，如果未找到则返回 None
        """
        # 获取音频文件的基础名称（不含扩展名）
        audio_name = Path(audio_path).stem

        # 可能的文稿文件扩展名
        possible_extensions = ['.txt', '.srt', '.vtt', '.json']

        self.logger.info(f"查找转录文件，音频文件名: {audio_name}")
        self.logger.info(f"输出目录: {output_dir}")

        # 方法1：精确匹配
        for ext in possible_extensions:
            transcript_file = os.path.join(output_dir, f"{audio_name}{ext}")
            self.logger.info(f"检查文件: {transcript_file}")
            self.logger.info(f"文件路径长度: {len(transcript_file)}")

            # 检查文件是否存在
            exists = os.path.exists(transcript_file)
            self.logger.info(f"文件存在: {exists}")

            if exists:
                self.logger.info(f"找到转录文件: {transcript_file}")
                return transcript_file
            else:
                # 尝试使用Path对象检查
                try:
                    path_obj = Path(transcript_file)
                    exists_path = path_obj.exists()
                    self.logger.info(f"Path对象检查存在: {exists_path}")
                    if exists_path:
                        return str(path_obj)
                except Exception as e:
                    self.logger.info(f"Path对象检查失败: {e}")

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
                    self.logger.info(f"检查变体文件: {transcript_file}")
                    if os.path.exists(transcript_file):
                        self.logger.info(f"找到变体转录文件: {transcript_file}")
                        return transcript_file

        # 方法2：检查whisper可能生成的变体文件名
        # whisper-ctranslate2有时会截断或修改文件名
        output_path = Path(output_dir)
        self.logger.info(f"尝试查找whisper可能生成的变体文件名")

        # 尝试不同长度的文件名前缀
        for prefix_len in [len(audio_name), len(audio_name) - 10, len(audio_name) - 20]:
            if prefix_len > 10:  # 确保前缀足够长
                prefix = audio_name[:prefix_len]
                self.logger.info(f"尝试前缀: {prefix}")

                for file_path in output_path.glob(f"{prefix}*.txt"):
                    # 检查文件是否是最近生成的（5分钟内）
                    import time
                    if time.time() - file_path.stat().st_mtime < 300:
                        self.logger.info(f"找到可能的转录文件: {file_path}")
                        return str(file_path)

        # 方法3：查找最新的文本文件（仅限最近5分钟内生成的文件）
        self.logger.info("尝试查找最近生成的文本文件")
        import time
        current_time = time.time()
        recent_files = []

        for ext in ['.txt', '.srt', '.vtt']:
            for file_path in output_path.glob(f"*{ext}"):
                file_mtime = file_path.stat().st_mtime
                # 只考虑最近5分钟内修改的文件
                if current_time - file_mtime < 300:  # 300秒 = 5分钟
                    recent_files.append(file_path)
                    self.logger.info(f"发现最近文件: {file_path} (修改时间: {time.ctime(file_mtime)})")

        if recent_files:
            # 按修改时间排序，取最新的
            latest_file = max(recent_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"选择最新的最近文件: {latest_file}")
            return str(latest_file)
        else:
            self.logger.info("未找到最近5分钟内生成的文本文件")

        # 列出输出目录中的所有文件，帮助调试
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
        str: 生成的文稿文件路径
    """
    transcriber = WhisperTranscriber()
    return transcriber.run_whisper(audio_path, output_dir)
