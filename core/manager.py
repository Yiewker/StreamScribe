"""
任务管理器

顶层调度器，接收UI层的请求，识别URL平台，并将任务分发给具体的平台处理器。
"""

import logging
import os
from pathlib import Path
from .config import get_config
from .utils import extract_video_id_from_url, validate_url, generate_output_filename
from .platform.youtube import YouTubeHandler
from .platform.local import LocalFileHandler
from .platform.bilibili import BilibiliHandler


class TaskManager:
    """任务管理器类"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # 初始化平台处理器
        self.platform_handlers = {
            'youtube': YouTubeHandler(),
            'bilibili': BilibiliHandler(),
            'local': LocalFileHandler()
        }
    
    def process_url(self, url, status_callback=None):
        """
        处理视频 URL，生成文稿
        
        Args:
            url (str): 视频 URL
            status_callback (callable): 状态回调函数，用于更新 UI
            
        Returns:
            dict: 处理结果，包含成功状态、文稿文件路径、错误信息等
        """
        result = {
            'success': False,
            'transcript_file': None,
            'error': None,
            'platform': None,
            'video_title': None
        }
        
        try:
            # 更新状态：开始处理
            if status_callback:
                status_callback("开始处理视频链接...")
            
            # 验证 URL 格式
            if not validate_url(url):
                raise ValueError("无效的 URL 格式")
            
            # 识别平台和视频 ID
            platform, video_id = extract_video_id_from_url(url)
            
            if not platform:
                raise ValueError("不支持的视频平台或无效的 URL")
            
            result['platform'] = platform
            
            # 更新状态：识别平台
            if status_callback:
                status_callback(f"识别到平台: {platform.upper()}")
            
            # 获取对应的平台处理器
            handler = self.platform_handlers.get(platform)
            if not handler:
                raise ValueError(f"暂不支持 {platform} 平台")
            
            # 调用平台处理器获取文稿
            transcript_result = handler.get_transcript(url, status_callback)
            
            if not transcript_result['success']:
                raise Exception(transcript_result['error'])
            
            result.update(transcript_result)
            result['success'] = True
            
            # 更新状态：处理完成
            if status_callback:
                status_callback("文稿生成完成！")
            
            self.logger.info(f"成功处理视频: {url}")
            
        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            self.logger.error(f"处理视频失败: {error_msg}")
            
            if status_callback:
                status_callback(f"处理失败: {error_msg}")
        
        return result
    
    def get_supported_platforms(self):
        """
        获取支持的平台列表
        
        Returns:
            list: 支持的平台名称列表
        """
        return list(self.platform_handlers.keys())
    
    def add_platform_handler(self, platform_name, handler):
        """
        添加新的平台处理器
        
        Args:
            platform_name (str): 平台名称
            handler: 平台处理器实例
        """
        self.platform_handlers[platform_name] = handler
        self.logger.info(f"添加平台处理器: {platform_name}")
    
    def remove_platform_handler(self, platform_name):
        """
        移除平台处理器
        
        Args:
            platform_name (str): 平台名称
        """
        if platform_name in self.platform_handlers:
            del self.platform_handlers[platform_name]
            self.logger.info(f"移除平台处理器: {platform_name}")
    
    def get_platform_info(self, url):
        """
        获取 URL 对应的平台信息
        
        Args:
            url (str): 视频 URL
            
        Returns:
            dict: 平台信息，包含平台名称、视频ID等
        """
        platform, video_id = extract_video_id_from_url(url)
        
        return {
            'platform': platform,
            'video_id': video_id,
            'supported': platform in self.platform_handlers
        }

    def process_local_file(self, file_path, status_callback=None):
        """
        处理本地文件

        Args:
            file_path (str): 本地文件路径
            status_callback (callable): 状态回调函数

        Returns:
            dict: 处理结果
        """
        try:
            self.logger.info(f"开始处理本地文件: {file_path}")

            # 使用本地文件处理器
            handler = self.platform_handlers['local']
            result = handler.get_transcript(file_path, status_callback)

            if result['success']:
                self.logger.info(f"成功处理本地文件: {file_path}")
            else:
                self.logger.error(f"处理本地文件失败: {result['error']}")

            return result

        except Exception as e:
            error_msg = f"处理本地文件时发生错误: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'file_name': os.path.basename(file_path),
                'transcript_file': None
            }

    def process_batch_urls(self, urls, status_callback=None):
        """
        批量处理 URL 列表

        Args:
            urls (list): URL 列表
            status_callback (callable): 状态回调函数

        Returns:
            dict: 批量处理结果
        """
        results = []
        total_count = len(urls)
        success_count = 0

        for i, url in enumerate(urls, 1):
            if status_callback:
                status_callback(f"处理第 {i}/{total_count} 个链接: {url}")

            result = self.process_url(url, status_callback)
            results.append(result)

            if result['success']:
                success_count += 1

        return {
            'success': success_count > 0,
            'total_count': total_count,
            'success_count': success_count,
            'failed_count': total_count - success_count,
            'results': results
        }

    def process_batch_files(self, file_paths, status_callback=None):
        """
        批量处理本地文件列表

        Args:
            file_paths (list): 文件路径列表
            status_callback (callable): 状态回调函数

        Returns:
            dict: 批量处理结果
        """
        results = []
        total_count = len(file_paths)
        success_count = 0

        for i, file_path in enumerate(file_paths, 1):
            if status_callback:
                status_callback(f"处理第 {i}/{total_count} 个文件: {os.path.basename(file_path)}")

            result = self.process_local_file(file_path, status_callback)
            results.append(result)

            if result['success']:
                success_count += 1

        return {
            'success': success_count > 0,
            'total_count': total_count,
            'success_count': success_count,
            'failed_count': total_count - success_count,
            'results': results
        }


# 便捷函数
def process_video_url(url, status_callback=None):
    """
    处理视频 URL 的便捷函数
    
    Args:
        url (str): 视频 URL
        status_callback (callable): 状态回调函数
        
    Returns:
        dict: 处理结果
    """
    manager = TaskManager()
    return manager.process_url(url, status_callback)
