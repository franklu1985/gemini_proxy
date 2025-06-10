#!/usr/bin/env python3
"""
生产环境诊断脚本
用于检查环境配置和依赖问题
"""

import os
import sys
import traceback
from pathlib import Path

def print_section(title):
    """打印节标题"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def check_python_environment():
    """检查Python环境"""
    print_section("Python环境检查")
    
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"Python路径列表: {sys.path[:5]}...")  # 只显示前5个
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {Path(__file__).parent.absolute()}")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境: 是")
        print(f"   虚拟环境路径: {sys.prefix}")
    else:
        print("⚠️  虚拟环境: 否 (建议使用虚拟环境)")
    
    # 检测宝塔面板虚拟环境
    venv_paths = [
        "/www/server/pyproject_evn/gemini_proxy_venv/bin/python",
        "/www/server/pyproject_envs/gemini_proxy_venv/bin/python",
        "/www/pyproject_envs/gemini_proxy_venv/bin/python",
        "/www/server/python_venv/gemini_proxy_venv/bin/python",
        "./venv/bin/python",
        "./.venv/bin/python"
    ]
    
    print("\n🔍 检查宝塔面板虚拟环境:")
    found_venv = False
    for venv_path in venv_paths:
        if os.path.exists(venv_path):
            print(f"✅ 找到虚拟环境: {venv_path}")
            found_venv = True
    
    if not found_venv:
        print("❌ 未找到宝塔面板虚拟环境")
        print("💡 建议在宝塔面板 -> Python项目管理器 中创建项目")

def check_dependencies():
    """检查依赖包"""
    print_section("依赖包检查")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'gunicorn',
        'google.genai',
        'pydantic',
        'python-dotenv',
        'python-multipart'
    ]
    
    for package in required_packages:
        try:
            if package == 'google.genai':
                import google.genai as genai
                print(f"✅ {package}: 已安装")
            else:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}: 已安装")
        except ImportError as e:
            print(f"❌ {package}: 未安装 - {e}")

def check_project_files():
    """检查项目文件"""
    print_section("项目文件检查")
    
    required_files = [
        'main.py',
        'config.py',
        'wsgi.py',
        'bt_gunicorn.conf.py',
        'requirements.txt',
        '.env'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: 存在")
        else:
            print(f"❌ {file}: 不存在")

def check_directories():
    """检查目录权限"""
    print_section("目录权限检查")
    
    directories = ['logs', 'audio_output']
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            if os.access(dir_name, os.W_OK):
                print(f"✅ {dir_name}: 存在且可写")
            else:
                print(f"⚠️  {dir_name}: 存在但不可写")
        else:
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ {dir_name}: 创建成功")
            except Exception as e:
                print(f"❌ {dir_name}: 创建失败 - {e}")

def check_environment_variables():
    """检查环境变量"""
    print_section("环境变量检查")
    
    if os.path.exists('.env'):
        print("✅ .env文件存在")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('GEMINI_API_KEY', '')
            if api_key and api_key != 'your_gemini_api_key_here':
                print("✅ GEMINI_API_KEY: 已配置")
            else:
                print("❌ GEMINI_API_KEY: 未配置或使用默认值")
            
            host = os.getenv('HOST', '0.0.0.0')
            port = os.getenv('PORT', '8000')
            print(f"ℹ️  服务器配置: {host}:{port}")
            
        except Exception as e:
            print(f"❌ 读取环境变量失败: {e}")
    else:
        print("❌ .env文件不存在")

def test_app_import():
    """测试应用导入"""
    print_section("应用导入测试")
    
    # 添加项目路径到Python路径
    project_root = Path(__file__).parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        print("正在测试config模块...")
        import config
        print("✅ config模块导入成功")
        
        print("正在测试main模块...")
        import main
        print("✅ main模块导入成功")
        
        print("正在测试FastAPI应用...")
        app = main.app
        if hasattr(app, 'openapi'):
            print("✅ FastAPI应用创建成功")
        else:
            print("❌ FastAPI应用创建失败")
            
        print("正在测试wsgi模块...")
        import wsgi
        if hasattr(wsgi, 'application'):
            print("✅ WSGI应用创建成功")
        else:
            print("❌ WSGI应用创建失败")
            
    except Exception as e:
        print(f"❌ 应用导入失败: {e}")
        print("\n详细错误信息:")
        traceback.print_exc()

def test_gunicorn_config():
    """测试Gunicorn配置"""
    print_section("Gunicorn配置测试")
    
    try:
        print("正在测试bt_gunicorn.conf.py...")
        
        # 模拟加载配置文件
        config_path = 'bt_gunicorn.conf.py'
        if os.path.exists(config_path):
            print("✅ 配置文件存在")
            
            # 读取配置内容
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'bind' in content:
                print("✅ bind配置存在")
            if 'worker_class' in content:
                print("✅ worker_class配置存在")
            if 'uvicorn.workers.UvicornWorker' in content:
                print("✅ UvicornWorker配置正确")
        else:
            print("❌ 配置文件不存在")
            
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")

def main():
    """主函数"""
    print("🚀 Gemini代理服务 - 生产环境诊断工具")
    print("=" * 50)
    
    check_python_environment()
    check_dependencies()
    check_project_files()
    check_directories()
    check_environment_variables()
    test_app_import()
    test_gunicorn_config()
    
    print_section("诊断完成")
    print("📝 如果发现问题，请根据上述检查结果进行修复")
    print("💡 常见解决方案:")
    print("   1. 安装缺失的依赖: pip install -r requirements.txt")
    print("   2. 配置API密钥: 编辑.env文件")
    print("   3. 检查文件权限: chown -R www:www /path/to/project")
    print("   4. 重新创建虚拟环境")

if __name__ == "__main__":
    main() 