"""
YouTube 平台处理器

包含所有与 YouTube 相关的操作逻辑，如检查字幕、调用 yt-dlp 下载等。
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from ..config import get_config
from ..utils import parse_vtt, generate_output_filename, sanitize_filename
from ..transcriber import WhisperTranscriber


class YouTubeHandler:
    """YouTube 平台处理器类"""
    
    def __init__(self):
        """初始化 YouTube 处理器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.transcriber = WhisperTranscriber()
        self.debug_callback = None

    def set_debug_callback(self, callback):
        """设置调试回调函数"""
        self.debug_callback = callback
        # 同时设置给转录器
        self.transcriber.set_debug_callback(callback)

    def _debug_log(self, message):
        """调试日志"""
        if self.debug_callback:
            self.debug_callback(message)
    
    def get_transcript(self, url, status_callback=None):
        """
        获取 YouTube 视频的文稿

        Args:
            url (str): YouTube 视频 URL
            status_callback (callable): 状态回调函数

        Returns:
            dict: 处理结果
        """
        result = {
            'success': False,
            'transcript_file': None,
            'error': None,
            'video_title': None,
            'method': None,  # 'subtitle' 或 'whisper'
            'processing_time': None,
            'audio_duration': None,
            'speed_ratio': None
        }
        
        try:
            # 更新状态
            if status_callback:
                status_callback("获取视频信息...")
            
            # 获取视频信息
            video_info = self._get_video_info(url)
            result['video_title'] = video_info.get('title', 'Unknown')
            
            # 检查是否启用强制转录模式
            force_transcribe = self.config.getboolean('general', 'force_transcribe_mode', False)

            if force_transcribe:
                # 强制转录模式：跳过字幕检测，直接使用AI转录
                result['method'] = 'whisper'
                if status_callback:
                    status_callback("强制转录模式：跳过字幕检测，直接使用AI转录...")

                # 下载音频文件
                audio_file = self._download_audio(url, video_info)

                # 使用 Whisper 转录
                if status_callback:
                    status_callback("正在使用 AI 转录音频...")

                transcribe_result = self._transcribe_audio(audio_file)
                transcript_file = transcribe_result['transcript_file']
                result['processing_time'] = transcribe_result['processing_time']
                result['audio_duration'] = transcribe_result['audio_duration']
                result['speed_ratio'] = transcribe_result['speed_ratio']
            else:
                # 正常模式：先检查字幕
                if status_callback:
                    status_callback("检查字幕可用性...")

                # 检查是否有字幕
                best_subtitle_lang = self._check_subtitles(url)

                if best_subtitle_lang:
                    # 使用字幕方式
                    result['method'] = 'subtitle'
                    if status_callback:
                        status_callback(f"发现字幕 ({best_subtitle_lang})，正在下载...")

                    transcript_file = self._download_subtitles(url, video_info, best_subtitle_lang)
                else:
                    # 使用 Whisper 转录方式
                    result['method'] = 'whisper'
                    if status_callback:
                        status_callback("未发现字幕，正在下载音频...")

                    audio_file = self._download_audio(url, video_info)

                    if status_callback:
                        status_callback("正在使用 AI 转录音频...")

                    transcribe_result = self._transcribe_audio(audio_file)
                    transcript_file = transcribe_result['transcript_file']
                    result['processing_time'] = transcribe_result['processing_time']
                    result['audio_duration'] = transcribe_result['audio_duration']
                    result['speed_ratio'] = transcribe_result['speed_ratio']

                    # 清理临时音频文件
                    try:
                        os.remove(audio_file)
                    except:
                        pass

            # 清理临时音频文件（强制转录模式）
            if force_transcribe:
                try:
                    os.remove(audio_file)
                except:
                    pass
            
            result['transcript_file'] = transcript_file
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"YouTube 处理失败: {str(e)}")
        
        return result
    
    def _get_video_info(self, url):
        """
        获取视频信息

        Args:
            url (str): 视频 URL

        Returns:
            dict: 视频信息
        """
        # 重试机制：最多重试3次
        max_retries = 3
        retry_delay = [2, 5, 10]  # 递增延迟时间

        for attempt in range(max_retries):
            try:
                command = [
                    self.config.yt_dlp_path,
                    '--dump-json',
                    '--no-download',
                    url
                ]

                # 添加代理设置（在重试时可能尝试不使用代理）
                if self.config.proxy and attempt < 2:  # 前两次尝试使用代理
                    command.extend(['--proxy', self.config.proxy])
                elif attempt >= 2:  # 第三次尝试不使用代理
                    print("🔄 尝试不使用代理...")

                # 添加额外的反检测参数
                command.extend([
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '--referer', 'https://www.youtube.com/',
                    '--sleep-interval', '1',
                    '--max-sleep-interval', '3',
                    '--no-check-certificate'
                ])

                # 打印完整命令供用户复制测试
                command_str = ' '.join(command)
                if attempt == 0:  # 只在第一次尝试时打印
                    print(f"\n🔍 执行 yt-dlp 获取视频信息:")
                    print(f"📋 {command_str}")
                    print()

                    # 发送到调试窗口
                    self._debug_log(f"🔍 执行 yt-dlp 获取视频信息:")
                    self._debug_log(f"📋 {command_str}")
                elif attempt > 0:
                    retry_msg = f"🔄 重试第 {attempt + 1} 次..."
                    print(retry_msg)
                    self._debug_log(retry_msg)

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=False,  # 使用字节模式避免编码问题
                    timeout=120  # 增加超时时间
                )

                if result.returncode != 0:
                    # 尝试解码错误信息
                    error_msg = "获取视频信息失败"
                    try:
                        error_msg = result.stderr.decode('utf-8', errors='ignore')
                    except:
                        try:
                            error_msg = result.stderr.decode('gbk', errors='ignore')
                        except:
                            pass

                    # 检查是否是可重试的错误
                    if self._is_retryable_error(error_msg) and attempt < max_retries - 1:
                        print(f"⚠️ 遇到可重试错误，{retry_delay[attempt]}秒后重试: {error_msg.strip()}")
                        import time
                        time.sleep(retry_delay[attempt])
                        continue
                    else:
                        raise Exception(f"获取视频信息失败: {error_msg}")

                # 尝试不同编码解码输出
                json_text = None
                for encoding in ['utf-8', 'gbk', 'cp936']:
                    try:
                        json_text = result.stdout.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue

                if not json_text:
                    raise Exception("无法解码视频信息")

                return json.loads(json_text)

            except subprocess.TimeoutExpired:
                if attempt < max_retries - 1:
                    print(f"⚠️ 请求超时，{retry_delay[attempt]}秒后重试...")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    raise Exception("获取视频信息超时")
            except json.JSONDecodeError:
                if attempt < max_retries - 1:
                    print(f"⚠️ JSON解析失败，{retry_delay[attempt]}秒后重试...")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    raise Exception("解析视频信息失败")
            except Exception as e:
                if self._is_retryable_error(str(e)) and attempt < max_retries - 1:
                    print(f"⚠️ 遇到错误，{retry_delay[attempt]}秒后重试: {str(e)}")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    raise e

        # 如果所有重试都失败了
        raise Exception("获取视频信息失败：已达到最大重试次数")

    def _is_retryable_error(self, error_msg):
        """
        判断错误是否可重试

        Args:
            error_msg (str): 错误信息

        Returns:
            bool: 是否可重试
        """
        retryable_errors = [
            "HTTP Error 403: Forbidden",
            "fragment 1 not found",
            "EOF occurred in violation of protocol",
            "Connection reset by peer",
            "Temporary failure in name resolution",
            "timeout",
            "Network is unreachable"
        ]

        error_msg_lower = error_msg.lower()
        return any(retryable_error.lower() in error_msg_lower for retryable_error in retryable_errors)
    
    def _check_subtitles(self, url):
        """
        检查视频是否有字幕，并返回最佳字幕语言

        Args:
            url (str): 视频 URL

        Returns:
            str or None: 最佳字幕语言代码，如果没有字幕则返回 None
        """
        # 重试机制：最多重试2次（字幕检查不需要太多重试）
        max_retries = 2
        retry_delay = [2, 5]

        for attempt in range(max_retries):
            try:
                command = [
                    self.config.yt_dlp_path,
                    '--list-subs',
                    url
                ]

                # 添加代理设置
                if self.config.proxy:
                    command.extend(['--proxy', self.config.proxy])

                # 添加额外的反检测参数
                command.extend([
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '--referer', 'https://www.youtube.com/'
                ])

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=False,  # 使用字节模式避免编码问题
                    timeout=60  # 增加超时时间
                )

                if result.returncode != 0:
                    if attempt < max_retries - 1:
                        print(f"⚠️ 获取字幕列表失败，{retry_delay[attempt]}秒后重试...")
                        import time
                        time.sleep(retry_delay[attempt])
                        continue
                    else:
                        self.logger.warning("获取字幕列表失败")
                        return None

                # 尝试不同的编码解码输出
                output_text = None
                for encoding in ['utf-8', 'gbk', 'cp936', 'latin1']:
                    try:
                        output_text = result.stdout.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue

                if not output_text:
                    if attempt < max_retries - 1:
                        print(f"⚠️ 无法解码字幕列表输出，{retry_delay[attempt]}秒后重试...")
                        import time
                        time.sleep(retry_delay[attempt])
                        continue
                    else:
                        self.logger.warning("无法解码字幕列表输出")
                        return None

                # 解析可用的字幕语言
                available_subs = self._parse_subtitle_languages(output_text)

                if not available_subs:
                    return None

                # 按优先级选择字幕
                return self._select_best_subtitle(available_subs)

            except subprocess.TimeoutExpired:
                if attempt < max_retries - 1:
                    print(f"⚠️ 检查字幕超时，{retry_delay[attempt]}秒后重试...")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    self.logger.warning("检查字幕超时，假设无字幕")
                    return None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ 检查字幕失败，{retry_delay[attempt]}秒后重试: {str(e)}")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    self.logger.warning(f"检查字幕失败: {str(e)}，假设无字幕")
                    return None

        # 如果所有重试都失败了，假设无字幕
        return None

    def _parse_subtitle_languages(self, output_text):
        """
        解析字幕列表输出，提取可用的语言代码

        Args:
            output_text (str): yt-dlp --list-subs 的输出

        Returns:
            list: 可用的字幕语言代码列表
        """
        available_subs = []
        lines = output_text.split('\n')

        # 查找字幕部分
        in_subtitle_section = False
        in_auto_caption_section = False

        for line in lines:
            line = line.strip()

            # 检测手动字幕部分开始
            if 'available subtitles' in line.lower():
                in_subtitle_section = True
                in_auto_caption_section = False
                continue

            # 检测自动字幕部分开始
            if 'available automatic captions' in line.lower():
                in_auto_caption_section = True
                in_subtitle_section = False
                continue

            # 跳过表头行
            if line.startswith('Language') and 'Name' in line and 'Formats' in line:
                continue

            # 解析字幕行
            if (in_subtitle_section or in_auto_caption_section) and line:
                # 字幕行格式: "语言代码    名称    格式..."
                # 使用空白字符分割，取第一个作为语言代码
                parts = line.split()
                if parts and not line.startswith('['):  # 排除日志行
                    lang_code = parts[0]
                    # 过滤掉明显不是语言代码的内容
                    if len(lang_code) <= 10 and '-' in lang_code or len(lang_code) <= 5:
                        if lang_code not in available_subs:
                            available_subs.append(lang_code)

        self.logger.info(f"发现可用字幕: {available_subs}")
        return available_subs

    def _select_best_subtitle(self, available_subs):
        """
        根据优先级选择最佳字幕

        优先级: Chinese (Simplified) > Chinese (Traditional) > English > 其他语言

        Args:
            available_subs (list): 可用的字幕语言代码列表

        Returns:
            str: 选择的字幕语言代码
        """
        # 定义优先级映射
        priority_map = {
            # 中文简体
            'zh-Hans': 1, 'zh-CN': 1, 'zh': 1, 'zh-Hant-CN': 1,
            # 中文繁体
            'zh-Hant': 2, 'zh-TW': 2, 'zh-HK': 2, 'zh-Hant-TW': 2, 'zh-Hant-HK': 2,
            # 英语
            'en': 3, 'en-US': 3, 'en-GB': 3, 'en-AU': 3, 'en-CA': 3,
        }

        # 按优先级排序
        best_sub = None
        best_priority = float('inf')

        for sub in available_subs:
            priority = priority_map.get(sub, 999)  # 其他语言优先级为999
            if priority < best_priority:
                best_priority = priority
                best_sub = sub

        self.logger.info(f"选择字幕语言: {best_sub} (优先级: {best_priority})")
        return best_sub
    
    def _download_subtitles(self, url, video_info, subtitle_lang):
        """
        下载字幕文件

        Args:
            url (str): 视频 URL
            video_info (dict): 视频信息
            subtitle_lang (str): 字幕语言代码

        Returns:
            str: 文稿文件路径
        """
        # 生成输出文件名
        filename = generate_output_filename(video_info.get('title', 'video'), 'youtube')
        
        # 设置输出路径
        output_template = os.path.join(self.config.temp_dir, f"{filename}.%(ext)s")
        
        command = [
            self.config.yt_dlp_path,
            '--write-subs',
            '--write-auto-subs',
            '--sub-lang', subtitle_lang,
            '--sub-format', 'vtt',
            '--skip-download',
            '--output', output_template,
            url
        ]
        
        # 添加代理设置
        if self.config.proxy:
            command.extend(['--proxy', self.config.proxy])
        
        try:
            # 打印完整命令供用户复制测试
            print(f"\n🔍 执行 yt-dlp 下载字幕:")
            print(f"📋 {' '.join(command)}")
            print()

            result = subprocess.run(
                command,
                capture_output=True,
                text=False,  # 使用字节模式避免编码问题
                timeout=300
            )

            if result.returncode != 0:
                # 尝试解码错误信息
                error_msg = "下载字幕失败"
                try:
                    error_msg = result.stderr.decode('utf-8', errors='ignore')
                except:
                    try:
                        error_msg = result.stderr.decode('gbk', errors='ignore')
                    except:
                        pass
                raise Exception(f"下载字幕失败: {error_msg}")

            # 查找下载的 VTT 文件
            vtt_file = self._find_vtt_file(self.config.temp_dir, filename)

            if not vtt_file:
                raise Exception("未找到下载的字幕文件")

            # 解析 VTT 文件为纯文本
            transcript_text = parse_vtt(vtt_file)

            # 保存为文本文件
            transcript_file = os.path.join(self.config.output_dir, f"{filename}.txt")
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            # 清理临时 VTT 文件
            try:
                os.remove(vtt_file)
            except:
                pass

            return transcript_file

        except subprocess.TimeoutExpired:
            raise Exception("下载字幕超时")
    
    def _download_audio(self, url, video_info):
        """
        下载音频文件

        Args:
            url (str): 视频 URL
            video_info (dict): 视频信息

        Returns:
            str: 音频文件路径
        """
        # 生成输出文件名
        filename = generate_output_filename(video_info.get('title', 'video'), 'youtube')

        # 设置输出路径
        output_template = os.path.join(self.config.temp_dir, f"{filename}.%(ext)s")

        # 重试机制：最多重试3次
        max_retries = 3
        retry_delay = [5, 10, 20]  # 递增延迟时间

        for attempt in range(max_retries):
            try:
                command = [
                    self.config.yt_dlp_path,
                    '--extract-audio',
                    '--audio-format', 'mp3',
                    '--audio-quality', '192K',
                    '--format', 'bestaudio/best',  # 优先选择最佳音频格式
                    '--no-video',  # 不下载视频
                    '--output', output_template,
                    url
                ]

                # 添加代理设置（在重试时可能尝试不使用代理）
                if self.config.proxy and attempt < 2:  # 前两次尝试使用代理
                    command.extend(['--proxy', self.config.proxy])
                elif attempt >= 2:  # 第三次尝试不使用代理
                    print("🔄 尝试不使用代理...")

                # 添加额外的反检测参数
                command.extend([
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    '--referer', 'https://www.youtube.com/',
                    '--sleep-interval', '1',
                    '--max-sleep-interval', '3',
                    '--retries', '3',
                    '--no-check-certificate'
                ])

                # 打印完整命令供用户复制测试
                if attempt == 0:  # 只在第一次尝试时打印
                    print(f"\n🔍 执行 yt-dlp 下载音频:")
                    print(f"📋 {' '.join(command)}")
                    print()
                elif attempt > 0:
                    print(f"🔄 重试第 {attempt + 1} 次下载音频...")

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=False,  # 使用字节模式避免编码问题
                    timeout=1800  # 30分钟超时
                )

                if result.returncode != 0:
                    # 尝试解码错误信息
                    error_msg = "下载音频失败"
                    try:
                        error_msg = result.stderr.decode('utf-8', errors='ignore')
                    except:
                        try:
                            error_msg = result.stderr.decode('gbk', errors='ignore')
                        except:
                            pass

                    # 检查是否是可重试的错误
                    if self._is_retryable_error(error_msg) and attempt < max_retries - 1:
                        print(f"⚠️ 遇到可重试错误，{retry_delay[attempt]}秒后重试: {error_msg.strip()}")
                        import time
                        time.sleep(retry_delay[attempt])
                        continue
                    else:
                        raise Exception(f"下载音频失败: {error_msg}")

                # 查找下载的音频文件
                audio_file = os.path.join(self.config.temp_dir, f"{filename}.mp3")

                if not os.path.exists(audio_file):
                    if attempt < max_retries - 1:
                        print(f"⚠️ 未找到下载的音频文件，{retry_delay[attempt]}秒后重试...")
                        import time
                        time.sleep(retry_delay[attempt])
                        continue
                    else:
                        raise Exception("未找到下载的音频文件")

                return audio_file

            except subprocess.TimeoutExpired:
                if attempt < max_retries - 1:
                    print(f"⚠️ 下载超时，{retry_delay[attempt]}秒后重试...")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    raise Exception("下载音频超时")
            except Exception as e:
                if self._is_retryable_error(str(e)) and attempt < max_retries - 1:
                    print(f"⚠️ 遇到错误，{retry_delay[attempt]}秒后重试: {str(e)}")
                    import time
                    time.sleep(retry_delay[attempt])
                    continue
                else:
                    raise e

        # 如果所有重试都失败了
        raise Exception("下载音频失败：已达到最大重试次数")
    
    def _transcribe_audio(self, audio_file):
        """
        转录音频文件

        Args:
            audio_file (str): 音频文件路径

        Returns:
            dict: 包含transcript_file, processing_time, audio_duration, speed_ratio的字典
        """
        self.logger.info(f"开始转录音频文件: {audio_file}")
        self.logger.info(f"输出目录: {self.config.output_dir}")

        # 检查音频文件是否存在
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")

        # 获取文件信息
        file_size = os.path.getsize(audio_file)
        self.logger.info(f"音频文件大小: {file_size} 字节")

        try:
            result = self.transcriber.run_whisper(audio_file, self.config.output_dir)
            self.logger.info(f"转录完成，生成文件: {result['transcript_file']}")
            self.logger.info(f"处理时间: {result['processing_time']:.2f}秒, 加速倍率: {result['speed_ratio']:.2f}x")
            return result
        except Exception as e:
            self.logger.error(f"转录失败: {str(e)}")
            raise
    
    def _find_vtt_file(self, directory, base_filename):
        """
        查找 VTT 字幕文件
        
        Args:
            directory (str): 搜索目录
            base_filename (str): 基础文件名
            
        Returns:
            str: VTT 文件路径，如果未找到则返回 None
        """
        directory_path = Path(directory)
        
        # 可能的 VTT 文件模式
        patterns = [
            f"{base_filename}.*.vtt",
            f"{base_filename}.vtt"
        ]
        
        for pattern in patterns:
            for vtt_file in directory_path.glob(pattern):
                return str(vtt_file)
        
        return None
