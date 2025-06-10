#!/usr/bin/env python3
"""
生产环境启动脚本
使用Gunicorn + Uvicorn Workers运行FastAPI应用
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# 导入应用
from main import app

# ASGI应用对象
application = app

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    # 开发环境直接使用uvicorn
    uvicorn.run(
        "start_production:application",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    ) 