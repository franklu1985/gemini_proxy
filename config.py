import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # Gemini API 配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 语音合成配置
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "zh")
    DEFAULT_TLD: str = os.getenv("DEFAULT_TLD", "com")
    
    # 输出目录
    AUDIO_OUTPUT_DIR: str = "audio_output"
    
    # Gemini 模型配置
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    def __post_init__(self):
        # 确保音频输出目录存在
        os.makedirs(self.AUDIO_OUTPUT_DIR, exist_ok=True)

# 创建全局配置实例
settings = Settings()
settings.__post_init__() 