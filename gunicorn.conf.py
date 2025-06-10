# Gunicorn配置文件
import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# Worker进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 60
keepalive = 2

# 重启配置
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程命名
proc_name = "gemini_proxy"

# 用户权限（生产环境中根据需要设置）
# user = "www-data"
# group = "www-data"

# 临时目录
tmp_upload_dir = None

# 性能优化
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None

# 优雅重启
graceful_timeout = 30

# 安全设置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 守护进程模式
daemon = False  # 由service.sh管理守护进程模式

# 捕获输出
capture_output = True

# 启动时的钩子函数
def on_starting(server):
    """服务启动时的钩子"""
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    server.log.info("Gemini Proxy服务正在启动...")

def on_reload(server):
    """重载时的钩子"""
    server.log.info("Gemini Proxy服务正在重载...")

def worker_abort(worker):
    """Worker异常退出时的钩子"""
    worker.log.error(f"Worker {worker.pid} 异常退出") 