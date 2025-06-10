#!/bin/bash

# Gemini代理服务生产环境部署脚本

set -e

echo "🚀 开始部署Gemini代理服务..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $python_version"

# 安装依赖
echo "📦 安装依赖包..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env文件不存在，请创建并配置GEMINI_API_KEY"
    cp .env_example .env
    echo "📝 已创建.env文件模板，请编辑后重新运行"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录..."
mkdir -p audio_output
mkdir -p logs

# 检查配置
echo "🔍 检查配置..."
python3 -c "
import os
from config import settings
print(f'✅ HOST: {settings.HOST}')
print(f'✅ PORT: {settings.PORT}')
print(f'✅ 音频输出目录: {settings.AUDIO_OUTPUT_DIR}')
if settings.GEMINI_API_KEY:
    print('✅ Gemini API Key: 已配置')
else:
    print('❌ Gemini API Key: 未配置')
    exit(1)
"

echo "✅ 部署完成！"
echo ""
echo "🎯 启动方式："
echo "  开发环境: python3 main.py"
echo "  生产环境: gunicorn --config gunicorn.conf.py start_production:application"
echo "  后台运行: nohup gunicorn --config gunicorn.conf.py start_production:application > logs/app.log 2>&1 &"
echo ""
echo "📊 监控："
echo "  查看日志: tail -f logs/app.log"
echo "  查看进程: ps aux | grep gunicorn"
echo "  停止服务: pkill -f 'gunicorn.*gemini_proxy'" 