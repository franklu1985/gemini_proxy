# Gemini代理服务 - 生产环境部署指南

## 🎯 推荐部署方式

### 宝塔面板部署 - 最简单的方式 ⭐

如果您使用的是Ubuntu系统并安装了宝塔面板，**强烈推荐**使用我们专门为宝塔面板优化的部署方案：

1. **查看宝塔面板部署指南**: [bt_deploy.md](bt_deploy.md)
2. **使用一键部署脚本**: `bash bt_quick_install.sh`
3. **使用宝塔服务管理**: `./bt_service.sh start`

宝塔面板部署的优势：
- 🚀 一键部署，自动配置环境
- 🎛️ 图形化界面管理Python项目
- 🌐 内置Nginx反向代理配置
- 📊 实时监控和日志查看
- 🔒 SSL证书自动申请和配置
- 🛡️ 防火墙规则自动管理

## 📋 其他部署方式

如果您不使用宝塔面板，可以选择以下传统部署方式：

### 部署前准备

### 系统要求
- Linux服务器 (Ubuntu 18.04+ / CentOS 7+ / RHEL 7+)
- Python 3.8+
- 至少 2GB RAM
- 至少 10GB 磁盘空间

### 必要软件
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install python3 python3-pip git
# 或
sudo dnf install python3 python3-pip git
```

## 🚀 快速部署

### 1. 克隆项目
```bash
git clone <repository-url> /opt/gemini_proxy
cd /opt/gemini_proxy
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 运行部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. 配置环境变量
```bash
# 编辑.env文件，设置Gemini API Key
nano .env

# 示例配置：
GEMINI_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```

### 5. 启动服务
```bash
chmod +x service.sh
./service.sh start
```

## 🔧 详细配置

### Gunicorn配置
编辑 `gunicorn.conf.py` 调整以下参数：

```python
# Worker进程数（根据CPU核心数调整）
workers = multiprocessing.cpu_count() * 2 + 1

# 超时设置（根据需要调整）
timeout = 60

# 绑定地址和端口
bind = "0.0.0.0:8000"
```

### 服务管理脚本
使用 `service.sh` 管理服务：

```bash
# 启动服务
./service.sh start

# 停止服务
./service.sh stop

# 重启服务
./service.sh restart

# 查看状态
./service.sh status

# 查看日志
./service.sh logs
```

## 🔄 Systemd集成（推荐）

### 1. 安装systemd服务
```bash
# 修改服务文件中的路径
sudo nano gemini-proxy.service

# 复制到systemd目录
sudo cp gemini-proxy.service /etc/systemd/system/

# 重载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable gemini-proxy

# 启动服务
sudo systemctl start gemini-proxy
```

### 2. Systemd命令
```bash
# 查看服务状态
sudo systemctl status gemini-proxy

# 启动服务
sudo systemctl start gemini-proxy

# 停止服务
sudo systemctl stop gemini-proxy

# 重启服务
sudo systemctl restart gemini-proxy

# 查看日志
sudo journalctl -u gemini-proxy -f
```

## 📊 监控和维护

### 日志管理
```bash
# 查看应用日志
tail -f logs/error.log
tail -f logs/access.log

# 日志轮转（推荐使用logrotate）
sudo nano /etc/logrotate.d/gemini-proxy
```

### 性能监控
```bash
# 查看进程状态
ps aux | grep gunicorn

# 查看端口占用
netstat -tlnp | grep 8000

# 查看系统资源
top -p $(cat logs/gunicorn.pid)
```

### 健康检查
```bash
# 检查服务健康状态
curl http://localhost:8000/api/v1/health

# 完整功能测试
python3 test_client.py
```

## 🔒 安全配置

### 防火墙设置
```bash
# Ubuntu (ufw)
sudo ufw allow 8000
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### Nginx反向代理（推荐）
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    location /audio/ {
        proxy_pass http://127.0.0.1:8000/audio/;
        proxy_buffering off;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🚨 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查错误日志
cat logs/error.log

# 检查配置
python3 -c "from config import settings; print('配置OK')"

# 检查端口占用
lsof -i :8000
```

#### 2. Worker进程错误
```bash
# 减少worker数量
# 编辑 gunicorn.conf.py
workers = 1

# 增加超时时间
timeout = 120
```

#### 3. 内存不足
```bash
# 监控内存使用
free -h
ps aux --sort=-%mem | head

# 减少worker数量或增加系统内存
```

#### 4. API请求失败
```bash
# 检查Gemini API Key
python3 -c "
from services.gemini_service import gemini_service
import asyncio
asyncio.run(gemini_service.check_api_status())
"
```

### 日志分析
```bash
# 查看最近的错误
grep -i error logs/error.log | tail -20

# 查看访问统计
awk '{print $1}' logs/access.log | sort | uniq -c | sort -nr

# 查看响应时间
grep "200" logs/access.log | awk '{print $NF}' | sort -n
```

## 📈 性能优化

### 1. Worker调优
```python
# gunicorn.conf.py
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)  # 限制最大worker数
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
```

### 2. 系统优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化TCP参数
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
sysctl -p
```

### 3. 缓存优化
- 考虑使用Redis缓存频繁请求的结果
- 实现音频文件的CDN分发

## 🔄 更新部署

### 1. 更新代码
```bash
git pull origin main
```

### 2. 更新依赖
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 重启服务
```bash
./service.sh restart
# 或
sudo systemctl restart gemini-proxy
```

### 4. 验证更新
```bash
python3 test_client.py
```

## 📞 技术支持

如遇问题，请检查：
1. 日志文件 (`logs/error.log`, `logs/access.log`)
2. 系统资源使用情况
3. 网络连接状态
4. Gemini API服务状态

更多信息请参考项目的 `README.md` 和 `API_DOCS.md` 文档。 