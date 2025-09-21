"""
B站（Bilibili）视频处理器

使用 BBDown 下载 B站视频并提取文稿。
"""

import os
import subprocess
import logging
import re
from pathlib import Path
from ..config import get_config
from ..transcriber import WhisperTranscriber
from ..utils import sanitize_filename


class BilibiliHandler:
    """B站视频处理器类"""
    
    def __init__(self):
        """初始化B站处理器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.transcriber = WhisperTranscriber()
    
    def get_transcript(self, url, status_callback=None):
        """
        获取B站视频的文稿
        
        Args:
            url (str): B站视频链接
            status_callback (callable): 状态回调函数
            
        Returns:
            dict: 处理结果
        """
        result = {
            'success': False,
            'transcript_file': None,
            'error': None,
            'video_title': None,
            'method': 'whisper'  # B站视频总是使用 whisper 转录
        }
        
        try:
            # 更新状态
            if status_callback:
                status_callback("正在获取B站视频信息...")
            
            # 获取视频信息
            video_info = self._get_video_info(url)
            if not video_info:
                raise Exception("无法获取视频信息")
            
            result['video_title'] = video_info.get('title', 'Unknown')
            
            if status_callback:
                status_callback(f"视频标题: {result['video_title']}")
            
            # 检查是否有现成的字幕
            if status_callback:
                status_callback("检查是否有现成字幕...")

            subtitle_file = self._try_download_subtitle(url, video_info)
            if subtitle_file:
                result['transcript_file'] = subtitle_file
                result['success'] = True
                result['method'] = 'subtitle'

                if status_callback:
                    status_callback("找到现成字幕，处理完成！")

                self.logger.info(f"成功获取B站字幕: {url}")
                return result

            # 如果没有找到字幕，给出提示
            if status_callback:
                status_callback("未找到现成字幕（可能需要B站账号登录），将使用AI转录...")
            
            # 没有字幕，下载音频进行转录
            if status_callback:
                status_callback("未找到字幕，正在下载音频...")
            
            audio_file = self._download_audio(url, video_info)
            if not audio_file:
                raise Exception("音频下载失败")
            
            # 使用 Whisper 转录
            if status_callback:
                status_callback("正在使用 AI 转录音频...")
            
            transcript_file = self.transcriber.run_whisper(audio_file, self.config.output_dir)
            
            # 清理临时音频文件
            try:
                os.remove(audio_file)
            except:
                pass
            
            result['transcript_file'] = transcript_file
            result['success'] = True
            
            if status_callback:
                status_callback("文稿生成完成！")
            
            self.logger.info(f"成功处理B站视频: {url}")
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            self.logger.error(f"处理B站视频失败: {error_msg}")
            
            if status_callback:
                status_callback(f"处理失败: {error_msg}")
        
        return result
    
    def _get_video_info(self, url):
        """获取视频信息"""
        try:
            # BBDown 的正确命令格式：BBDown <url> --only-show-info
            command = [
                self.config.bbdown_path,
                url,
                '--only-show-info'
            ]

            print(f"\n🔍 获取B站视频信息:")
            print(f"📋 {' '.join(command)}")
            print()

            result = subprocess.run(
                command,
                capture_output=True,
                text=False,
                timeout=60
            )

            # 尝试解码输出
            output = ""
            for encoding in ['utf-8', 'gbk', 'cp936']:
                try:
                    output = result.stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if result.returncode == 0 and output:
                # 解析视频标题 - BBDown 输出格式：视频标题: xxx
                title_match = re.search(r'视频标题[:：]\s*(.+)', output)
                if title_match:
                    title = title_match.group(1).strip()
                    return {'title': title}

            # 如果解析失败，尝试从URL提取BV号作为标题
            bv_match = re.search(r'(BV[a-zA-Z0-9]+)', url)
            if bv_match:
                return {'title': bv_match.group(1)}

            return {'title': 'B站视频'}

        except Exception as e:
            self.logger.warning(f"获取B站视频信息失败: {e}")
            return {'title': 'B站视频'}
    
    def _try_download_subtitle(self, url, video_info):
        """尝试下载现成的字幕"""
        if not self.config.bbdown_download_subtitle:
            return None

        try:
            title = video_info.get('title', 'bilibili_video')
            safe_title = sanitize_filename(title)

            # 确保临时目录存在
            os.makedirs(self.config.temp_dir, exist_ok=True)

            # BBDown 的正确命令格式：BBDown <url> --sub-only --work-dir <dir>
            command = [
                self.config.bbdown_path,
                url,
                '--sub-only',
                '--work-dir', self.config.temp_dir
            ]

            print(f"\n🔍 尝试下载B站字幕:")
            print(f"📋 {' '.join(command)}")
            print()

            result = subprocess.run(
                command,
                capture_output=True,
                text=False,
                timeout=300
            )

            # 打印输出用于调试
            output = ""
            for encoding in ['utf-8', 'gbk', 'cp936']:
                try:
                    output = result.stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            print(f"BBDown 返回码: {result.returncode}")
            if output:
                print(f"BBDown 输出: {output[:200]}...")

            if result.returncode == 0:
                # 查找下载的字幕文件 - 扩大搜索范围
                subtitle_extensions = ['*.srt', '*.ass', '*.vtt', '*.xml']
                subtitle_files = []

                for ext in subtitle_extensions:
                    subtitle_files.extend(list(Path(self.config.temp_dir).glob(ext)))

                print(f"找到的字幕文件: {[f.name for f in subtitle_files]}")

                if subtitle_files:
                    # 选择第一个字幕文件
                    subtitle_file = subtitle_files[0]
                    output_file = os.path.join(self.config.output_dir, f"{safe_title}.txt")

                    # 根据文件类型转换
                    if subtitle_file.suffix.lower() == '.srt':
                        self._convert_srt_to_txt(str(subtitle_file), output_file)
                    elif subtitle_file.suffix.lower() == '.ass':
                        self._convert_ass_to_txt(str(subtitle_file), output_file)
                    elif subtitle_file.suffix.lower() == '.vtt':
                        self._convert_vtt_to_txt(str(subtitle_file), output_file)
                    else:
                        # 其他格式直接复制内容
                        with open(subtitle_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(content)

                    # 清理临时文件
                    try:
                        subtitle_file.unlink()
                    except:
                        pass

                    print(f"✅ 字幕转换完成: {output_file}")
                    return output_file
                else:
                    print("❌ 未找到字幕文件")
            else:
                print(f"❌ BBDown 执行失败，返回码: {result.returncode}")

            return None

        except Exception as e:
            self.logger.warning(f"下载B站字幕失败: {e}")
            print(f"❌ 字幕下载异常: {e}")
            return None
    
    def _download_audio(self, url, video_info):
        """下载音频文件"""
        try:
            title = video_info.get('title', 'bilibili_video')
            safe_title = sanitize_filename(title)

            # 确保临时目录存在
            os.makedirs(self.config.temp_dir, exist_ok=True)

            # BBDown 的正确命令格式：BBDown <url> --audio-only --work-dir <dir>
            command = [
                self.config.bbdown_path,
                url,
                '--audio-only',
                '--work-dir', self.config.temp_dir
            ]

            print(f"\n🔍 下载B站音频:")
            print(f"📋 {' '.join(command)}")
            print()

            result = subprocess.run(
                command,
                capture_output=True,
                text=False,
                timeout=1800  # 30分钟超时
            )

            # 打印输出用于调试
            output = ""
            for encoding in ['utf-8', 'gbk', 'cp936']:
                try:
                    output = result.stdout.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            print(f"BBDown 返回码: {result.returncode}")
            if output:
                print(f"BBDown 输出: {output[:200]}...")

            if result.returncode == 0:
                # 查找下载的音频文件 - 扩大搜索范围
                audio_extensions = ['*.mp3', '*.aac', '*.flac', '*.m4a', '*.wav']
                audio_files = []

                for ext in audio_extensions:
                    audio_files.extend(list(Path(self.config.temp_dir).glob(ext)))

                print(f"找到的音频文件: {[f.name for f in audio_files]}")

                if audio_files:
                    # 选择第一个音频文件
                    audio_file = audio_files[0]
                    print(f"✅ 音频下载完成: {audio_file}")
                    return str(audio_file)
                else:
                    print("❌ 未找到音频文件")
            else:
                print(f"❌ BBDown 执行失败，返回码: {result.returncode}")

            raise Exception("音频文件下载失败")

        except subprocess.TimeoutExpired:
            raise Exception("音频下载超时")
        except Exception as e:
            raise Exception(f"音频下载失败: {str(e)}")
    
    def _convert_srt_to_txt(self, srt_file, txt_file):
        """将 SRT 字幕转换为纯文本"""
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 移除时间戳和序号，只保留文本
            lines = content.split('\n')
            text_lines = []

            for line in lines:
                line = line.strip()
                # 跳过序号行和时间戳行
                if line and not line.isdigit() and '-->' not in line:
                    text_lines.append(line)

            # 写入纯文本文件
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_lines))

        except Exception as e:
            self.logger.error(f"转换SRT字幕文件失败: {e}")
            raise

    def _convert_ass_to_txt(self, ass_file, txt_file):
        """将 ASS 字幕转换为纯文本"""
        try:
            with open(ass_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # ASS 格式的对话行以 "Dialogue:" 开头
            lines = content.split('\n')
            text_lines = []

            for line in lines:
                line = line.strip()
                if line.startswith('Dialogue:'):
                    # ASS 格式：Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        text = parts[9].strip()
                        # 移除 ASS 格式标签
                        text = re.sub(r'\{[^}]*\}', '', text)
                        if text:
                            text_lines.append(text)

            # 写入纯文本文件
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_lines))

        except Exception as e:
            self.logger.error(f"转换ASS字幕文件失败: {e}")
            raise

    def _convert_vtt_to_txt(self, vtt_file, txt_file):
        """将 VTT 字幕转换为纯文本"""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # VTT 格式类似 SRT，但有 "WEBVTT" 头部
            lines = content.split('\n')
            text_lines = []

            for line in lines:
                line = line.strip()
                # 跳过 WEBVTT 头部、序号行、时间戳行和空行
                if (line and
                    not line.startswith('WEBVTT') and
                    not line.isdigit() and
                    '-->' not in line and
                    not line.startswith('NOTE')):
                    text_lines.append(line)

            # 写入纯文本文件
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(text_lines))

        except Exception as e:
            self.logger.error(f"转换VTT字幕文件失败: {e}")
            raise


# 便捷函数
def process_bilibili_url(url, status_callback=None):
    """
    处理B站视频的便捷函数
    
    Args:
        url (str): B站视频链接
        status_callback (callable): 状态回调函数
        
    Returns:
        dict: 处理结果
    """
    handler = BilibiliHandler()
    return handler.get_transcript(url, status_callback)
