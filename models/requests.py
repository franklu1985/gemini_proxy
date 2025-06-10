from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TextGenerationRequest(BaseModel):
    """文本生成请求模型"""
    prompt: str = Field(..., description="输入提示文本", min_length=1, max_length=10000)
    max_tokens: Optional[int] = Field(None, description="最大 token 数", ge=1, le=4000)
    temperature: float = Field(0.7, description="创造性参数", ge=0.0, le=1.0)
    top_p: float = Field(0.9, description="核心采样参数", ge=0.0, le=1.0)

class TextToSpeechRequest(BaseModel):
    """文本转语音请求模型"""
    text: str = Field(..., description="要转换的文本", min_length=1, max_length=5000)
    voice_name: Optional[str] = Field("Kore", description="声音名称，如: Kore, Puck, Zephyr")
    language: Optional[str] = Field(None, description="语言代码（可选，模型自动检测）")

class TextGenerationWithHistoryRequest(BaseModel):
    """基于历史的文本生成请求模型"""
    messages: List[Dict[str, str]] = Field(..., description="对话历史")
    max_tokens: Optional[int] = Field(None, description="最大 token 数", ge=1, le=4000)
    temperature: float = Field(0.7, description="创造性参数", ge=0.0, le=1.0)

class TextGenerationResponse(BaseModel):
    """文本生成响应模型"""
    success: bool = Field(..., description="是否成功")
    text: Optional[str] = Field(None, description="生成的文本")
    error: Optional[str] = Field(None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class TextToSpeechResponse(BaseModel):
    """文本转语音响应模型"""
    success: bool = Field(..., description="是否成功")
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    filename: Optional[str] = Field(None, description="音频文件名")
    error: Optional[str] = Field(None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class ApiStatusResponse(BaseModel):
    """API状态响应模型"""
    status: str = Field(..., description="状态: success/error")
    message: str = Field(..., description="状态信息")
    model: Optional[str] = Field(None, description="使用的模型")
    test_response: Optional[str] = Field(None, description="测试响应")

class LanguagesResponse(BaseModel):
    """支持语言响应模型"""
    success: bool = Field(..., description="是否成功")
    languages: Optional[Dict[str, str]] = Field(None, description="支持的语言列表")
    error: Optional[str] = Field(None, description="错误信息")

class CombinedRequest(BaseModel):
    """组合请求模型：生成文本并转换为语音"""
    prompt: str = Field(..., description="输入提示文本", min_length=1, max_length=10000)
    max_tokens: Optional[int] = Field(None, description="最大 token 数", ge=1, le=4000)
    temperature: float = Field(0.7, description="创造性参数", ge=0.0, le=1.0)
    voice_name: Optional[str] = Field("Kore", description="声音名称")
    language: Optional[str] = Field(None, description="语音语言代码（可选）")

class CombinedResponse(BaseModel):
    """组合响应模型"""
    success: bool = Field(..., description="是否成功")
    text: Optional[str] = Field(None, description="生成的文本")
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    filename: Optional[str] = Field(None, description="音频文件名")
    error: Optional[str] = Field(None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class SpeakerConfig(BaseModel):
    """说话人配置模型"""
    speaker: str = Field(..., description="说话人名称")
    voice_name: str = Field(..., description="声音名称")

class MultiSpeakerTTSRequest(BaseModel):
    """多说话人TTS请求模型"""
    text: str = Field(..., description="包含说话人标记的文本", min_length=1, max_length=5000)
    speaker_configs: List[SpeakerConfig] = Field(..., description="说话人配置列表")

class VoicesResponse(BaseModel):
    """声音列表响应模型"""
    success: bool = Field(..., description="是否成功")
    voices: Optional[List[str]] = Field(None, description="支持的声音列表")
    error: Optional[str] = Field(None, description="错误信息") 