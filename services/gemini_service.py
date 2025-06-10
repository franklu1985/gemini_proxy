import google.genai as genai
from typing import Optional, List, Dict, Any
from config import settings
import logging
import asyncio

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini AI 服务"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.client = None
        
        if self.api_key:
            self._initialize_client()
        else:
            logger.warning("Gemini API Key 未配置")
    
    def _initialize_client(self):
        """初始化 Gemini 客户端"""
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini 客户端初始化成功，使用模型: {self.model_name}")
        except Exception as e:
            logger.error(f"Gemini 客户端初始化失败: {str(e)}")
            self.client = None
            # 不要抛出异常，允许服务启动但返回错误信息
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示
            max_tokens: 最大 token 数
            temperature: 创造性参数 (0-1)
            top_p: 核心采样参数 (0-1)
            
        Returns:
            生成的文本
        """
        if not self.client:
            raise Exception("Gemini 客户端未初始化，请检查 API Key")
        
        try:
            # 配置生成参数
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # 在线程池中执行生成操作
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_content, 
                prompt, 
                generation_config
            )
            
            logger.info(f"成功生成文本，长度: {len(response)} 字符")
            return response
            
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise Exception(f"文本生成失败: {str(e)}")
    
    def _generate_content(self, prompt: str, generation_config: Dict[str, Any]) -> str:
        """在线程中生成内容，带重试机制"""
        import time
        import ssl
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # 根据官方文档使用正确的API调用格式
                from google.genai.types import GenerateContentConfig
                
                config = GenerateContentConfig(
                    temperature=generation_config.get("temperature", 0.7),
                    top_p=generation_config.get("top_p", 0.9),
                    max_output_tokens=generation_config.get("max_output_tokens")
                )
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                
                # 提取生成的文本
                if response.candidates and len(response.candidates) > 0:
                    if response.candidates[0].content and response.candidates[0].content.parts:
                        return response.candidates[0].content.parts[0].text
                
                raise Exception("未能从响应中获取文本内容")
                
            except ssl.SSLError as ssl_error:
                logger.warning(f"SSL错误 (尝试 {attempt + 1}/{max_retries}): {str(ssl_error)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise Exception(f"SSL连接失败，已重试{max_retries}次: {str(ssl_error)}")
            except Exception as e:
                if "ssl" in str(e).lower() or "unexpected_eof" in str(e).lower():
                    logger.warning(f"网络连接错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                
                logger.error(f"Gemini API 错误: {str(e)}")
                raise e
    
    async def generate_text_with_history(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> str:
        """
        基于对话历史生成文本
        
        Args:
            messages: 对话历史，格式: [{"role": "user/assistant", "content": "..."}]
            max_tokens: 最大 token 数
            temperature: 创造性参数
            
        Returns:
            生成的文本
        """
        if not self.client:
            raise Exception("Gemini 客户端未初始化，请检查 API Key")
        
        try:
            # 将历史消息转换为单个 prompt
            prompt = self._format_messages_to_prompt(messages)
            
            return await self.generate_text(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"基于历史的文本生成失败: {str(e)}")
            raise Exception(f"基于历史的文本生成失败: {str(e)}")
    
    def _format_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息历史格式化为 prompt"""
        formatted_messages = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "user":
                formatted_messages.append(f"用户: {content}")
            elif role == "assistant":
                formatted_messages.append(f"助手: {content}")
        
        # 添加最新的指令
        formatted_messages.append("请根据上述对话历史，生成合适的回复:")
        
        return "\n".join(formatted_messages)
    
    async def check_api_status(self) -> Dict[str, Any]:
        """检查 API 状态"""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "API Key 未配置"
                }
            
            if not self.client:
                return {
                    "status": "error", 
                    "message": "Gemini 客户端未初始化"
                }
            
            # 简单状态检查，不进行实际API调用以避免阻塞
            return {
                "status": "ready",
                "message": "服务已准备就绪",
                "model": self.model_name,
                "api_configured": bool(self.api_key),
                "client_initialized": bool(self.client)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"状态检查失败: {str(e)}"
            }

# 创建全局实例
gemini_service = GeminiService() 