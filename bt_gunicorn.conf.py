# 宝塔面板专用 Gunicorn配置文件
import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# Worker进程配置
workers = max(2, multiprocessing.cpu_count())  # 至少2个worker
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120  # 增加超时时间
keepalive = 2

# 重启配置
max_requests = 1000
max_requests_jitter = 50
preload_app = False  # 改为False避免导入问题

# 日志配置
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

accesslog = os.path.join(log_dir, "access.log")
errorlog = os.path.join(log_dir, "error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程命名
proc_name = "gemini_proxy_bt"

# 宝塔面板用户权限
user = "www"
group = "www"

# 临时目录
tmp_upload_dir = None

# 性能优化
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else "/tmp"

# 优雅重启
graceful_timeout = 30

# 安全设置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 守护进程模式
daemon = False

# 捕获输出
capture_output = True
enable_stdio_inheritance = True

# 错误处理
reload = False
reload_engine = "auto"

# 启动时的钩子函数
def on_starting(server):
    """服务启动时的钩子"""
    import sys
    from pathlib import Path
    
    # 确保项目路径在Python路径中
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    os.makedirs("audio_output", exist_ok=True)
    
    server.log.info("🚀 Gemini Proxy 宝塔部署版本启动中...")
    server.log.info(f"📁 项目路径: {project_root}")
    server.log.info(f"🐍 Python路径: {sys.path[:3]}...")

def on_reload(server):
    """重载时的钩子"""
    server.log.info("🔄 Gemini Proxy服务正在重载...")

def worker_abort(worker):
    """Worker异常退出时的钩子"""
    worker.log.error(f"💥 Worker {worker.pid} 异常退出")

def pre_fork(server, worker):
    """Fork worker前的钩子"""
    server.log.info(f"👷 启动 Worker {worker.age}")

def post_fork(server, worker):
    """Fork worker后的钩子"""
    server.log.info(f"✅ Worker {worker.pid} 已启动")

def worker_int(worker):
    """Worker收到中断信号时的钩子"""
    worker.log.info(f"⚠️ Worker {worker.pid} 收到中断信号")

# 宝塔面板特定配置
def when_ready(server):
    """服务就绪时的钩子"""
    server.log.info("🎉 Gemini Proxy 宝塔部署版本已就绪！")
    server.log.info(f"🌐 访问地址: http://0.0.0.0:8000")
    server.log.info(f"📚 API文档: http://0.0.0.0:8000/docs") 