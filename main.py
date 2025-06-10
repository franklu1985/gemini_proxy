from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import logging
import os
from contextlib import asynccontextmanager

from api.endpoints import router
from config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Gemini 代理服务启动中...")
    
    # 确保音频输出目录存在
    os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
    
    logger.info(f"服务器运行在 http://{settings.HOST}:{settings.PORT}")
    yield
    
    # 关闭时
    logger.info("Gemini 代理服务关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title="Gemini 代理服务",
    description="基于 Google Gemini API 的代理服务，支持文本生成和语音合成",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(router, prefix="/api/v1", tags=["main"])

# 挂载静态文件
if os.path.exists(settings.AUDIO_OUTPUT_DIR):
    app.mount("/audio", StaticFiles(directory=settings.AUDIO_OUTPUT_DIR), name="audio")

# 创建模板目录（如果需要）
templates_dir = "templates"
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """根路径 - 返回简单的API文档页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gemini 代理服务</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .api-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .endpoint { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #007bff; }
            .method { font-weight: bold; color: #007bff; }
            .url { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            .description { color: #666; margin-top: 5px; }
            .link { display: inline-block; margin: 10px 5px; padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
            .link:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Gemini 代理服务</h1>
            <p style="text-align: center; color: #666;">基于 Google Gemini API 的代理服务，支持文本生成和语音合成</p>
            
            <div class="api-section">
                <h2>📚 API 文档</h2>
                <a href="/docs" class="link">Swagger 文档</a>
                <a href="/redoc" class="link">ReDoc 文档</a>
            </div>
            
            <div class="api-section">
                <h2>🔧 主要功能</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/api/v1/generate</span>
                    <div class="description">生成文本 - 使用 Gemini AI 生成文本内容</div>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/api/v1/text_to_speech</span>
                    <div class="description">文本转语音 - 使用 Gemini 原生TTS语音合成</div>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/api/v1/multi_speaker_tts</span>
                    <div class="description">多说话人TTS - 使用 Gemini 原生多说话人语音合成</div>
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/api/v1/generate_and_speak</span>
                    <div class="description">生成文本并转语音 - 一站式服务</div>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <span class="url">/api/v1/status</span>
                    <div class="description">检查 API 状态</div>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <span class="url">/api/v1/voices</span>
                    <div class="description">获取 Gemini TTS 支持的声音列表</div>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <span class="url">/api/v1/languages</span>
                    <div class="description">获取 Gemini TTS 支持的语言列表</div>
                </div>
            </div>
            
            <div class="api-section">
                <h2>⚙️ 配置说明</h2>
                <p>1. 复制 <code>env_example.txt</code> 为 <code>.env</code></p>
                <p>2. 设置您的 <code>GEMINI_API_KEY</code></p>
                <p>3. 根据需要调整其他配置参数</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 错误处理"""
    return HTMLResponse(
        content="<h1>404 - 页面未找到</h1><p><a href='/'>返回首页</a></p>",
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """500 错误处理"""
    logger.error(f"服务器错误: {str(exc)}")
    return HTMLResponse(
        content="<h1>500 - 服务器内部错误</h1><p><a href='/'>返回首页</a></p>",
        status_code=500
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    ) 