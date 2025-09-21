#!/usr/bin/env python3
"""
StreamScribe 紧凑版主程序

使用重新设计的紧凑UI界面
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.utils import setup_logging
from ui_compact import StreamScribeCompactUI

def main():
    """主函数"""
    try:
        # 设置日志
        logger = setup_logging()
        logger.info("启动 StreamScribe 紧凑版")
        
        # 创建并运行UI
        app = StreamScribeCompactUI()
        app.run()
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
