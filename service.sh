#!/bin/bash

# Gemini代理服务管理脚本

APP_NAME="gemini_proxy"
APP_DIR=$(dirname $(readlink -f $0))
PID_FILE="$APP_DIR/logs/gunicorn.pid"
LOG_FILE="$APP_DIR/logs/app.log"
CONFIG_FILE="$APP_DIR/gunicorn.conf.py"
APP_MODULE="start_production:application"

cd $APP_DIR

start() {
    if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
        echo "❌ 服务已在运行中 (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    echo "🚀 启动 $APP_NAME 服务..."
    
    # 确保日志目录存在
    mkdir -p logs
    
    # 启动服务
    gunicorn --config $CONFIG_FILE --pid $PID_FILE --daemon $APP_MODULE
    
    if [ $? -eq 0 ]; then
        echo "✅ $APP_NAME 服务启动成功"
        echo "📄 PID文件: $PID_FILE"
        echo "📋 日志文件: $LOG_FILE"
    else
        echo "❌ $APP_NAME 服务启动失败"
        return 1
    fi
}

stop() {
    if [ ! -f $PID_FILE ]; then
        echo "❌ PID文件不存在，服务可能未运行"
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    echo "🛑 停止 $APP_NAME 服务 (PID: $PID)..."
    
    if kill -0 $PID 2>/dev/null; then
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
    sleep 2
    start
}

status() {
    if [ -f $PID_FILE ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
        PID=$(cat $PID_FILE)
        echo "✅ $APP_NAME 服务正在运行 (PID: $PID)"
        
        # 显示进程信息
        ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
        
        # 检查端口
        if command -v netstat >/dev/null 2>&1; then
            echo ""
            echo "📡 监听端口:"
            netstat -tlnp 2>/dev/null | grep $PID | head -5
        fi
        
        return 0
    else
        echo "❌ $APP_NAME 服务未运行"
        return 1
    fi
}

logs() {
    if [ -f $LOG_FILE ]; then
        echo "📋 查看 $APP_NAME 服务日志:"
        echo "----------------------------------------"
        tail -f $LOG_FILE
    else
        echo "❌ 日志文件不存在: $LOG_FILE"
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
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志"
        exit 1
        ;;
esac

exit $? 