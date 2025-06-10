#!/bin/bash

# 宝塔面板 Gemini代理服务管理脚本

APP_NAME="gemini_proxy"
APP_PATH="/www/wwwroot/gemini_proxy"
PYTHON_PATH="/www/server/python/3.8/bin"  # 根据实际Python版本调整
PID_FILE="$APP_PATH/logs/gunicorn.pid"
LOG_FILE="$APP_PATH/logs/error.log"
CONFIG_FILE="$APP_PATH/gunicorn.conf.py"
APP_MODULE="start_production:application"

# 检查是否在正确目录
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 项目目录不存在: $APP_PATH"
    echo "请先部署项目到宝塔面板"
    exit 1
fi

cd $APP_PATH

start() {
    if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
        echo "❌ $APP_NAME 服务已在运行中 (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    echo "🚀 启动 $APP_NAME 服务..."
    
    # 确保日志目录存在且权限正确
    mkdir -p logs
    chown -R www:www logs
    chown -R www:www audio_output 2>/dev/null || mkdir -p audio_output && chown -R www:www audio_output
    
    # 使用宝塔Python环境启动服务
    $PYTHON_PATH/gunicorn \
        --config $CONFIG_FILE \
        --pid $PID_FILE \
        --daemon \
        --user www \
        --group www \
        $APP_MODULE
    
    if [ $? -eq 0 ]; then
        sleep 2
        if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
            echo "✅ $APP_NAME 服务启动成功 (PID: $(cat $PID_FILE))"
            echo "📄 PID文件: $PID_FILE"
            echo "📋 日志文件: $LOG_FILE"
            echo "🌐 访问地址: http://localhost:8000"
        else
            echo "❌ $APP_NAME 服务启动失败，请检查日志"
            cat $LOG_FILE 2>/dev/null | tail -10
            return 1
        fi
    else
        echo "❌ $APP_NAME 服务启动失败"
        return 1
    fi
}

stop() {
    if [ ! -f $PID_FILE ]; then
        echo "❌ PID文件不存在，$APP_NAME 服务可能未运行"
        # 尝试查找并杀死相关进程
        PIDS=$(ps aux | grep "gunicorn.*$APP_MODULE" | grep -v grep | awk '{print $2}')
        if [ ! -z "$PIDS" ]; then
            echo "🔍 发现相关进程，正在清理..."
            echo $PIDS | xargs kill -TERM
            sleep 2
            echo $PIDS | xargs kill -KILL 2>/dev/null
            echo "✅ 进程清理完成"
        fi
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    echo "🛑 停止 $APP_NAME 服务 (PID: $PID)..."
    
    if kill -0 $PID 2>/dev/null; then
        # 优雅停止
        kill -TERM $PID
        
        # 等待进程结束
        for i in {1..30}; do
            if ! kill -0 $PID 2>/dev/null; then
                break
            fi
            echo "等待进程结束... ($i/30)"
            sleep 1
        done
        
        # 如果进程仍在运行，强制杀死
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  进程未响应，强制终止..."
            kill -KILL $PID
            sleep 1
        fi
        
        rm -f $PID_FILE
        echo "✅ $APP_NAME 服务已停止"
    else
        echo "❌ 进程不存在 (PID: $PID)"
        rm -f $PID_FILE
        return 1
    fi
}

restart() {
    echo "🔄 重启 $APP_NAME 服务..."
    stop
    sleep 3
    start
}

status() {
    if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
        PID=$(cat $PID_FILE)
        echo "✅ $APP_NAME 服务正在运行 (PID: $PID)"
        
        # 显示进程信息
        echo ""
        echo "📊 进程信息:"
        ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime --no-headers
        
        # 检查端口
        if command -v ss >/dev/null 2>&1; then
            echo ""
            echo "📡 监听端口:"
            ss -tlnp | grep ":8000"
        elif command -v netstat >/dev/null 2>&1; then
            echo ""
            echo "📡 监听端口:"
            netstat -tlnp 2>/dev/null | grep ":8000"
        fi
        
        # 检查健康状态
        echo ""
        echo "🏥 服务健康检查:"
        if command -v curl >/dev/null 2>&1; then
            curl -s -o /dev/null -w "状态码: %{http_code}\n" http://localhost:8000/api/v1/health
        else
            echo "curl 未安装，跳过健康检查"
        fi
        
        return 0
    else
        echo "❌ $APP_NAME 服务未运行"
        
        # 检查是否有遗留进程
        PIDS=$(ps aux | grep "gunicorn.*$APP_MODULE" | grep -v grep | awk '{print $2}')
        if [ ! -z "$PIDS" ]; then
            echo "⚠️  发现遗留进程: $PIDS"
            echo "建议运行: $0 stop 清理进程"
        fi
        
        return 1
    fi
}

logs() {
    if [ -f $LOG_FILE ]; then
        echo "📋 查看 $APP_NAME 服务日志 (最后50行):"
        echo "=========================================="
        tail -50 $LOG_FILE
        echo "=========================================="
        echo ""
        echo "💡 实时查看日志: tail -f $LOG_FILE"
        echo "💡 查看访问日志: tail -f $APP_PATH/logs/access.log"
    else
        echo "❌ 日志文件不存在: $LOG_FILE"
        echo "📁 日志目录内容:"
        ls -la $APP_PATH/logs/ 2>/dev/null || echo "日志目录不存在"
        return 1
    fi
}

check_env() {
    echo "🔍 检查运行环境..."
    
    # 检查Python版本
    if [ -x "$PYTHON_PATH/python" ]; then
        PYTHON_VERSION=$($PYTHON_PATH/python --version 2>&1)
        echo "✅ Python: $PYTHON_VERSION"
    else
        echo "❌ Python不存在: $PYTHON_PATH/python"
        echo "请检查宝塔面板Python安装"
        return 1
    fi
    
    # 检查Gunicorn
    if [ -x "$PYTHON_PATH/gunicorn" ]; then
        GUNICORN_VERSION=$($PYTHON_PATH/gunicorn --version 2>&1)
        echo "✅ Gunicorn: $GUNICORN_VERSION"
    else
        echo "❌ Gunicorn未安装"
        echo "请运行: $PYTHON_PATH/pip install gunicorn"
        return 1
    fi
    
    # 检查配置文件
    if [ -f "$CONFIG_FILE" ]; then
        echo "✅ 配置文件存在: $CONFIG_FILE"
    else
        echo "❌ 配置文件不存在: $CONFIG_FILE"
        return 1
    fi
    
    # 检查启动文件
    if [ -f "$APP_PATH/start_production.py" ]; then
        echo "✅ 启动文件存在: start_production.py"
    else
        echo "❌ 启动文件不存在: start_production.py"
        return 1
    fi
    
    # 检查环境变量
    if [ -f "$APP_PATH/.env" ]; then
        echo "✅ 环境变量文件存在: .env"
        if grep -q "GEMINI_API_KEY=" "$APP_PATH/.env"; then
            echo "✅ Gemini API Key已配置"
        else
            echo "⚠️  Gemini API Key未配置"
        fi
    else
        echo "❌ 环境变量文件不存在: .env"
        return 1
    fi
    
    # 检查目录权限
    if [ -w "$APP_PATH" ]; then
        echo "✅ 项目目录可写"
    else
        echo "⚠️  项目目录权限不足，建议运行: chown -R www:www $APP_PATH"
    fi
    
    echo "🎯 环境检查完成"
}

install_deps() {
    echo "📦 安装Python依赖..."
    if [ -f "$APP_PATH/requirements.txt" ]; then
        $PYTHON_PATH/pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            echo "✅ 依赖安装成功"
        else
            echo "❌ 依赖安装失败"
            return 1
        fi
    else
        echo "❌ requirements.txt 文件不存在"
        return 1
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    check)
        check_env
        ;;
    install)
        install_deps
        ;;
    *)
        echo "宝塔面板 Gemini代理服务管理脚本"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs|check|install}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志"
        echo "  check   - 检查运行环境"
        echo "  install - 安装Python依赖"
        echo ""
        echo "示例:"
        echo "  $0 start     # 启动服务"
        echo "  $0 status    # 查看状态"
        echo "  $0 logs      # 查看日志"
        exit 1
        ;;
esac

exit $? 