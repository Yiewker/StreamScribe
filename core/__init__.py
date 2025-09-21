"""
StreamScribe Core Package

这个包包含了 StreamScribe 应用程序的所有核心后端逻辑。

模块说明:
- config: 配置文件加载和管理
- manager: 任务管理和平台分发
- transcriber: AI 转录功能
- utils: 通用工具函数
- platform: 平台特定的处理逻辑
"""

__version__ = "1.0.0"
__author__ = "StreamScribe Team"

# 导出主要的类和函数，方便外部调用
from .manager import TaskManager
from .config import Config

__all__ = ['TaskManager', 'Config']
