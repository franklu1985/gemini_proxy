#!/bin/bash

# 宝塔面板 Gemini代理服务一键部署脚本

echo "🚀 宝塔面板 Gemini代理服务一键部署脚本"
echo "==========================================="

# 配置变量
APP_NAME="gemini_proxy"
WEB_ROOT="/www/wwwroot"
APP_PATH="$WEB_ROOT/$APP_NAME"
PYTHON_VERSION=""  # 将自动检测
PYTHON_PATH=""     # 将自动检测虚拟环境路径

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        log_info "sudo bash $0"
        exit 1
    fi
}

# 检查宝塔面板
check_bt_panel() {
    log_info "检查宝塔面板..."
    if [ ! -d "/www/server/panel" ]; then
        log_error "未检测到宝塔面板，请先安装宝塔面板"
        log_info "安装宝塔面板: curl -sSO https://download.bt.cn/install/install_panel.sh && bash install_panel.sh"
        exit 1
    fi
    log_success "宝塔面板已安装"
}

# 检测宝塔面板虚拟环境
detect_bt_python_env() {
    # 宝塔面板虚拟环境可能的路径
    local venv_paths=(
        "/www/server/pyproject_evn/${APP_NAME}_venv/bin"
        "/www/server/pyproject_envs/${APP_NAME}_venv/bin"
        "/www/pyproject_envs/${APP_NAME}_venv/bin"
        "/www/server/python_venv/${APP_NAME}_venv/bin"
        "$APP_PATH/venv/bin"
        "$APP_PATH/.venv/bin"
    )
    
    for venv_path in "${venv_paths[@]}"; do
        if [ -x "$venv_path/python" ]; then
            echo "$venv_path"
            return 0
        fi
    done
    
    # 如果找不到虚拟环境，尝试系统Python
    for version in 3.12 3.11 3.10 3.9 3.8; do
        local sys_path="/www/server/python/$version/bin"
        if [ -x "$sys_path/python" ]; then
            echo "$sys_path"
            PYTHON_VERSION=$version
            return 0
        fi
    done
    
    return 1
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    PYTHON_PATH=$(detect_bt_python_env)
    
    if [ -z "$PYTHON_PATH" ]; then
        log_warning "未找到Python虚拟环境或系统Python"
        log_info "请先在宝塔面板中配置Python环境："
        log_info "1. 进入 '软件商店' -> '运行环境' -> 安装Python"
        log_info "2. 进入 'Python项目管理器' -> '添加Python项目'"
        log_info "3. 设置项目路径为: $APP_PATH"
        
        # 尝试引导用户选择Python版本
        log_info "或者，现在为您检查可用的Python版本..."
        for version in 3.12 3.11 3.10 3.9 3.8; do
            if [ -x "/www/server/python/$version/bin/python" ]; then
                log_info "发现Python $version，是否创建虚拟环境？(y/n)"
                read -r create_venv
                if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
                    PYTHON_VERSION=$version
                    PYTHON_PATH="/www/server/python/$version/bin"
                    
                    # 创建虚拟环境
                    log_info "为项目创建虚拟环境..."
                    $PYTHON_PATH/python -m venv "$APP_PATH/venv"
                    PYTHON_PATH="$APP_PATH/venv/bin"
                    log_success "虚拟环境创建成功: $PYTHON_PATH"
                    break
                fi
            fi
        done
        
        if [ -z "$PYTHON_PATH" ]; then
            log_error "未找到可用的Python版本或虚拟环境"
            log_error "请在宝塔面板中正确配置Python环境后重试"
            exit 1
        fi
    fi
    
    PYTHON_VER=$($PYTHON_PATH/python --version 2>&1)
    log_success "Python环境检查通过: $PYTHON_VER"
    log_info "Python路径: $PYTHON_PATH"
    
    # 检查是否为虚拟环境
    if echo "$PYTHON_PATH" | grep -q "venv\|envs"; then
        log_success "使用虚拟环境: 是"
    else
        log_warning "使用虚拟环境: 否 (建议使用虚拟环境)"
    fi
}

# 创建项目目录
create_project_dir() {
    log_info "创建项目目录..."
    
    if [ -d "$APP_PATH" ]; then
        log_warning "项目目录已存在: $APP_PATH"
        log_info "是否删除现有目录重新部署？(y/n)"
        read -r recreate
        if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
            rm -rf "$APP_PATH"
            log_info "已删除现有目录"
        else
            log_info "使用现有目录继续部署"
        fi
    fi
    
    mkdir -p "$APP_PATH"
    cd "$APP_PATH"
    log_success "项目目录创建完成: $APP_PATH"
}

# 设置目录权限
set_permissions() {
    log_info "设置目录权限..."
    chown -R www:www "$APP_PATH"
    chmod -R 755 "$APP_PATH"
    
    # 创建必要的子目录
    mkdir -p "$APP_PATH/logs"
    mkdir -p "$APP_PATH/audio_output"
    chown -R www:www "$APP_PATH/logs"
    chown -R www:www "$APP_PATH/audio_output"
    
    log_success "目录权限设置完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt 文件不存在"
        log_info "请确保已上传完整的项目文件"
        exit 1
    fi
    
    # 升级pip
    $PYTHON_PATH/pip install --upgrade pip
    
    # 安装依赖
    $PYTHON_PATH/pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        log_success "依赖安装完成"
    else
        log_error "依赖安装失败"
        exit 1
    fi
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env_example" ]; then
            cp .env_example .env
            log_info "已创建.env文件，请配置以下参数："
        else
            # 创建基本的.env文件
            cat > .env << EOF
# Gemini API配置
GEMINI_API_KEY=your_gemini_api_key_here

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 音频输出目录
AUDIO_OUTPUT_DIR=audio_output

# 日志配置
LOG_LEVEL=INFO
EOF
            log_info "已创建.env文件模板，请配置以下参数："
        fi
        
        echo ""
        echo "请编辑 $APP_PATH/.env 文件，设置以下参数："
        echo "1. GEMINI_API_KEY - 您的Gemini API密钥"
        echo "2. 其他配置参数（可选）"
        echo ""
        echo "是否现在编辑配置文件？(y/n)"
        read -r edit_config
        if [ "$edit_config" = "y" ] || [ "$edit_config" = "Y" ]; then
            if command -v nano >/dev/null 2>&1; then
                nano .env
            elif command -v vim >/dev/null 2>&1; then
                vim .env
            else
                log_warning "未找到文本编辑器，请手动编辑 $APP_PATH/.env"
            fi
        fi
    else
        log_success "环境变量文件已存在"
    fi
}

# 更新宝塔服务脚本中的Python路径
update_service_script() {
    log_info "更新服务管理脚本..."
    
    if [ -f "bt_service.sh" ]; then
        # 更新Python路径
        sed -i "s|PYTHON_PATH=\"/www/server/python/3.8/bin\"|PYTHON_PATH=\"$PYTHON_PATH\"|g" bt_service.sh
        chmod +x bt_service.sh
        log_success "服务管理脚本已更新"
    else
        log_warning "bt_service.sh 文件不存在"
    fi
}

# 测试服务
test_service() {
    log_info "测试服务启动..."
    
    # 检查服务脚本
    if [ -f "bt_service.sh" ]; then
        ./bt_service.sh check
        if [ $? -eq 0 ]; then
            log_success "环境检查通过"
            
            # 尝试启动服务
            log_info "启动服务进行测试..."
            ./bt_service.sh start
            
            if [ $? -eq 0 ]; then
                sleep 5
                
                # 测试健康检查
                if command -v curl >/dev/null 2>&1; then
                    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
                    if [ "$HEALTH_CHECK" = "200" ]; then
                        log_success "服务启动成功，健康检查通过"
                    else
                        log_warning "服务启动但健康检查失败 (状态码: $HEALTH_CHECK)"
                    fi
                else
                    log_info "curl未安装，跳过健康检查"
                fi
                
                # 停止测试服务
                ./bt_service.sh stop
                log_info "测试完成，服务已停止"
            else
                log_error "服务启动失败，请检查日志"
            fi
        else
            log_error "环境检查失败"
        fi
    else
        log_warning "服务管理脚本不存在，跳过服务测试"
    fi
}

# 创建宝塔面板网站
create_bt_site() {
    log_info "提供宝塔面板配置指导..."
    
    echo ""
    echo "🌐 宝塔面板网站配置"
    echo "=================================="
    echo "1. 登录宝塔面板"
    echo "2. 进入 '网站' 页面"
    echo "3. 点击 '添加站点'"
    echo "4. 配置如下："
    echo "   - 域名: 您的域名 (如: gemini.yourdomain.com)"
    echo "   - 根目录: $APP_PATH"
    echo "   - 不创建数据库和FTP"
    echo "5. 创建网站后，进入网站设置"
    echo "6. 配置反向代理:"
    echo "   - 代理名称: gemini_proxy"
    echo "   - 目标URL: http://127.0.0.1:8000"
    echo ""
    
    echo "📋 Python项目管理器配置"
    echo "=================================="
    echo "1. 进入 'Python项目管理器'"
    echo "2. 点击 '添加Python项目'"
    echo "3. 配置如下："
    echo "   - 项目名称: $APP_NAME"
    echo "   - Python版本: $PYTHON_VERSION"
    echo "   - 项目路径: $APP_PATH"
    echo "   - 启动文件: start_production.py"
    echo "   - 启动方式: Gunicorn"
    echo "   - 端口: 8000"
    echo ""
}

# 显示完成信息
show_completion() {
    echo ""
    echo "🎉 部署完成！"
    echo "=================================="
    echo "项目路径: $APP_PATH"
    echo "Python版本: $PYTHON_VERSION"
    echo "服务管理: ./bt_service.sh {start|stop|restart|status|logs}"
    echo ""
    echo "📝 下一步操作："
    echo "1. 配置Gemini API密钥: 编辑 $APP_PATH/.env"
    echo "2. 在宝塔面板中配置Python项目或网站反向代理"
    echo "3. 启动服务: $APP_PATH/bt_service.sh start"
    echo "4. 查看状态: $APP_PATH/bt_service.sh status"
    echo "5. 访问API文档: http://your-domain/docs"
    echo ""
    echo "🔗 有用的链接："
    echo "- 健康检查: http://localhost:8000/api/v1/health"
    echo "- API文档: http://localhost:8000/docs"
    echo "- 项目日志: $APP_PATH/logs/"
    echo ""
    echo "⚠️  重要提醒："
    echo "- 请确保在宝塔面板中正确配置防火墙规则"
    echo "- 建议配置SSL证书以启用HTTPS"
    echo "- 定期备份配置和日志文件"
}

# 主函数
main() {
    echo ""
    log_info "开始一键部署..."
    
    # 检查环境
    check_root
    check_bt_panel
    check_python
    
    # 如果当前不在项目目录，询问是否创建
    if [ ! -f "requirements.txt" ] && [ ! -f "main.py" ]; then
        log_warning "当前目录不是Gemini代理项目目录"
        log_info "请确保已将项目文件上传到服务器"
        log_info "是否在 $APP_PATH 创建项目目录？(y/n)"
        read -r create_dir
        if [ "$create_dir" = "y" ] || [ "$create_dir" = "Y" ]; then
            create_project_dir
            log_error "请将项目文件上传到 $APP_PATH 后重新运行此脚本"
            exit 1
        else
            log_error "请在项目根目录运行此脚本"
            exit 1
        fi
    fi
    
    # 部署步骤
    set_permissions
    install_dependencies
    setup_environment
    update_service_script
    test_service
    create_bt_site
    show_completion
    
    log_success "一键部署完成！"
}

# 执行主函数
main "$@" 