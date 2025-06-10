#!/usr/bin/env python3
"""
WSGI入口文件 - 用于Gunicorn生产环境部署
"""

import os
import sys
from pathlib import Path

# 设置项目根目录
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('PYTHONPATH', str(project_root))

try:
    # 导入FastAPI应用
    from main import app
    
    # WSGI应用对象（Gunicorn需要）
    application = app
    
    # 验证应用是否正确加载
    if hasattr(app, 'openapi'):
        print("✅ FastAPI应用成功加载")
    else:
        print("❌ FastAPI应用加载失败")
        
except Exception as e:
    print(f"❌ 应用加载错误: {e}")
    import traceback
    traceback.print_exc()
    # 创建一个简单的错误应用
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [f'应用加载失败: {str(e)}'.encode('utf-8')] 