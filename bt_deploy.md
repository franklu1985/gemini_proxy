# 宝塔面板部署 Gemini 代理服务指南

## 📋 准备工作

### 1. 宝塔面板环境要求
- Ubuntu 18.04+ 系统
- 宝塔面板 7.0+
- Python 3.8+ (通过宝塔安装)
- 至少 2GB 内存

### 2. 宝塔面板必装软件
在宝塔面板 `软件商店` 中安装：
- **Nginx** - Web服务器/反向代理
- **Python项目管理器** - Python环境管理
- **进程守护管理器** - 服务进程管理
- **文件管理器** - 文件操作

## 🚀 部署步骤

### 第一步：上传项目文件

1. 在宝塔面板 **文件管理** 中，进入 `/www/wwwroot/`
2. 创建项目目录：`mkdir gemini_proxy`
3. 上传项目文件到 `/www/wwwroot/gemini_proxy/`

或使用Git克隆：
```bash
cd /www/wwwroot/
git clone <your-repo-url> gemini_proxy
cd gemini_proxy
```

### 第二步：Python环境配置

1. 进入宝塔面板 **Python项目管理器**
2. 点击 **添加Python项目**
3. 配置如下：
   - **项目名称**: `gemini_proxy`
   - **Python版本**: `3.8+`
   - **项目路径**: `/www/wwwroot/gemini_proxy`
   - **启动文件**: `start_production.py`
   - **启动方式**: `Gunicorn`
   - **端口**: `8000`

### 第三步：安装依赖

在 **Python项目管理器** 中点击项目的 **模块** 按钮：

```bash
# 或者在SSH终端中执行
cd /www/wwwroot/gemini_proxy
pip install -r requirements.txt
```

### 第四步：环境变量配置

1. 复制环境变量模板：
```bash
cp .env_example .env
```

2. 编辑 `.env` 文件：
```bash
GEMINI_API_KEY=your_gemini_api_key_here
HOST=0.0.0.0
PORT=8000
AUDIO_OUTPUT_DIR=audio_output
```

### 第五步：目录权限设置

```bash
# 设置项目目录权限
chown -R www:www /www/wwwroot/gemini_proxy
chmod -R 755 /www/wwwroot/gemini_proxy

# 创建必要目录
mkdir -p /www/wwwroot/gemini_proxy/audio_output
mkdir -p /www/wwwroot/gemini_proxy/logs
chown -R www:www /www/wwwroot/gemini_proxy/audio_output
chown -R www:www /www/wwwroot/gemini_proxy/logs
```

## 🔧 宝塔面板配置

### 方式一：使用Python项目管理器（推荐）

1. 在 **Python项目管理器** 中找到 `gemini_proxy` 项目
2. 点击 **设置** 配置启动参数：
   ```
   启动文件: start_production.py
   端口: 8000
   启动方式: Gunicorn
   进程数: auto
   ```
3. 点击 **启动** 开始运行服务

### 方式二：使用进程守护管理器

1. 进入 **进程守护管理器**
2. 点击 **添加守护进程**
3. 配置如下：
   - **名称**: `gemini_proxy`
   - **启动用户**: `www`
   - **启动命令**: 
     ```bash
     /www/server/python/3.8/bin/gunicorn --config /www/wwwroot/gemini_proxy/gunicorn.conf.py start_production:application
     ```
   - **进程目录**: `/www/wwwroot/gemini_proxy`

### 方式三：自定义守护进程脚本

创建宝塔专用的启动脚本：

```bash
#!/bin/bash
# /www/wwwroot/gemini_proxy/bt_start.sh

cd /www/wwwroot/gemini_proxy
source /www/server/python/3.8/bin/activate

# 使用宝塔Python环境
/www/server/python/3.8/bin/gunicorn \
    --config gunicorn.conf.py \
    --pid logs/gunicorn.pid \
    --daemon \
    start_production:application

echo "Gemini Proxy 服务已启动"
```

## 🌐 Nginx 反向代理配置

### 1. 创建站点

在宝塔面板 **网站** 中：
1. 点击 **添加站点**
2. 配置域名（如：`gemini.yoursite.com`）
3. 不创建数据库和FTP

### 2. 配置反向代理

在站点设置中找到 **反向代理**：

```nginx
# 代理名称: gemini_proxy
# 目标URL: http://127.0.0.1:8000

location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_buffering off;
}

# 音频文件特殊处理
location /audio/ {
    proxy_pass http://127.0.0.1:8000/audio/;
    proxy_buffering off;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### 3. SSL证书配置（推荐）

在站点设置的 **SSL** 选项中：
1. 申请Let's Encrypt免费证书
2. 或上传自有证书
3. 开启强制HTTPS

## 📊 监控和管理

### 宝塔面板监控

1. **系统监控**：查看CPU、内存、磁盘使用情况
2. **进程管理**：在进程守护管理器中查看服务状态
3. **日志查看**：
   ```bash
   # 应用日志
   tail -f /www/wwwroot/gemini_proxy/logs/error.log
   
   # Nginx访问日志  
   tail -f /www/server/panel/logs/access.log
   ```

### 自动化脚本

创建宝塔专用的管理脚本：

```bash
#!/bin/bash
# /www/wwwroot/gemini_proxy/bt_service.sh

APP_PATH="/www/wwwroot/gemini_proxy"
PID_FILE="$APP_PATH/logs/gunicorn.pid"

case "$1" in
    start)
        cd $APP_PATH
        /www/server/python/3.8/bin/gunicorn \
            --config gunicorn.conf.py \
            --pid $PID_FILE \
            --daemon \
            start_production:application
        echo "✅ 服务已启动"
        ;;
    stop)
        if [ -f $PID_FILE ]; then
            kill $(cat $PID_FILE)
            rm -f $PID_FILE
            echo "✅ 服务已停止"
        else
            echo "❌ 服务未运行"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
            echo "✅ 服务正在运行 (PID: $(cat $PID_FILE))"
        else
            echo "❌ 服务未运行"
        fi
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        ;;
esac
```

## 🔒 安全配置

### 防火墙设置

在宝塔面板 **安全** 中：
1. 开放端口 `8000`（内网访问）
2. 如果使用域名访问，可以关闭8000端口的外网访问
3. 开放HTTP(80)和HTTPS(443)端口

### 访问限制

在Nginx配置中添加IP白名单（可选）：
```nginx
# 限制管理接口访问
location /docs {
    allow 192.168.1.0/24;  # 允许内网访问
    allow YOUR_IP_ADDRESS;  # 允许特定IP
    deny all;
}

location /redoc {
    allow 192.168.1.0/24;
    allow YOUR_IP_ADDRESS;
    deny all;
}
```

## 🚨 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 检查Python环境
   /www/server/python/3.8/bin/python --version
   
   # 检查依赖
   cd /www/wwwroot/gemini_proxy
   /www/server/python/3.8/bin/pip list
   
   # 查看错误日志
   tail -f logs/error.log
   ```

2. **端口冲突**
   ```bash
   # 查看端口占用
   netstat -tlnp | grep 8000
   
   # 修改配置文件中的端口
   nano gunicorn.conf.py
   ```

3. **权限问题**
   ```bash
   # 重新设置权限
   chown -R www:www /www/wwwroot/gemini_proxy
   chmod +x /www/wwwroot/gemini_proxy/bt_service.sh
   ```

4. **Nginx配置错误**
   - 在宝塔面板检查Nginx配置语法
   - 重启Nginx服务
   - 查看Nginx错误日志

### 性能优化

1. **调整Gunicorn配置**：
   ```python
   # 根据服务器配置调整
   workers = 4  # 根据CPU核心数
   worker_connections = 1000
   ```

2. **Nginx缓存配置**：
   ```nginx
   # 静态文件缓存
   location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
       expires 1M;
       add_header Cache-Control "public, immutable";
   }
   ```

## 📈 维护和更新

### 定期维护

1. **日志清理**：
   ```bash
   # 创建定时任务清理日志
   find /www/wwwroot/gemini_proxy/logs -name "*.log" -mtime +7 -delete
   ```

2. **依赖更新**：
   ```bash
   cd /www/wwwroot/gemini_proxy
   /www/server/python/3.8/bin/pip install --upgrade -r requirements.txt
   ```

3. **代码更新**：
   ```bash
   cd /www/wwwroot/gemini_proxy
   git pull origin main
   ./bt_service.sh restart
   ```

### 宝塔面板计划任务

在宝塔面板 **计划任务** 中添加：

1. **每日重启服务**（可选）：
   ```bash
   /www/wwwroot/gemini_proxy/bt_service.sh restart
   ```

2. **每周清理日志**：
   ```bash
   find /www/wwwroot/gemini_proxy/logs -name "*.log" -mtime +7 -delete
   ```

3. **健康检查**：
   ```bash
   curl -f http://localhost:8000/api/v1/health || /www/wwwroot/gemini_proxy/bt_service.sh restart
   ```

## 🎯 访问服务

部署完成后，您可以通过以下方式访问：

- **API文档**: `https://your-domain.com/docs`
- **健康检查**: `https://your-domain.com/api/v1/health`
- **直接端口访问**: `http://your-server-ip:8000`（如果防火墙允许）

现在您的Gemini代理服务已经成功部署在宝塔面板上了！ 