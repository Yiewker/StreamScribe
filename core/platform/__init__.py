"""
StreamScribe Platform Package

这个包包含了各个视频平台的特定处理逻辑。

当前支持的平台:
- YouTube (youtube.py)

未来计划支持:
- Bilibili
- 其他视频平台
"""

from .youtube import YouTubeHandler

__all__ = ['YouTubeHandler']
