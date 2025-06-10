from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any
import os
import logging

from models.requests import (
    TextGenerationRequest, TextGenerationResponse,
    TextToSpeechRequest, TextToSpeechResponse,
    TextGenerationWithHistoryRequest, ApiStatusResponse,
    LanguagesResponse, CombinedRequest, CombinedResponse,
    MultiSpeakerTTSRequest, VoicesResponse
)
from services.gemini_service import gemini_service
from services.gemini_tts_service import gemini_tts_service
from config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """生成文本"""
    try:
        text = await gemini_service.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        return TextGenerationResponse(
            success=True,
            text=text,
            metadata={
                "prompt_length": len(request.prompt),
                "response_length": len(text),
                "temperature": request.temperature,
                "top_p": request.top_p
            }
        )
    except Exception as e:
        logger.error(f"文本生成错误: {str(e)}")
        return TextGenerationResponse(
            success=False,
            error=str(e)
        )

@router.post("/generate_with_history", response_model=TextGenerationResponse)
async def generate_text_with_history(request: TextGenerationWithHistoryRequest):
    """基于对话历史生成文本"""
    try:
        text = await gemini_service.generate_text_with_history(
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return TextGenerationResponse(
            success=True,
            text=text,
            metadata={
                "history_length": len(request.messages),
                "response_length": len(text),
                "temperature": request.temperature
            }
        )
    except Exception as e:
        logger.error(f"基于历史的文本生成错误: {str(e)}")
        return TextGenerationResponse(
            success=False,
            error=str(e)
        )

@router.post("/text_to_speech", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest, background_tasks: BackgroundTasks):
    """文本转语音 - 使用Gemini TTS"""
    try:
        # 使用 Gemini TTS
        audio_path = await gemini_tts_service.generate_speech(
            text=request.text,
            voice_name=request.voice_name,
            language=request.language
        )
        # 在后台任务中清理旧文件
        background_tasks.add_task(gemini_tts_service.cleanup_old_files, 100)
        
        metadata = {
            "text_length": len(request.text),
            "voice_name": request.voice_name,
            "language": request.language or "auto",
            "tts_engine": "gemini"
        }
        
        # 获取文件名
        filename = os.path.basename(audio_path)
        
        return TextToSpeechResponse(
            success=True,
            audio_url=f"/audio/{filename}",
            filename=filename,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"语音合成错误: {str(e)}")
        return TextToSpeechResponse(
            success=False,
            error=str(e)
        )

@router.post("/generate_and_speak", response_model=CombinedResponse)
async def generate_and_speak(request: CombinedRequest, background_tasks: BackgroundTasks):
    """生成文本并转换为语音 - 使用Gemini TTS"""
    try:
        # 生成文本
        text = await gemini_service.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # 转换为语音 - 使用 Gemini TTS
        audio_path = await gemini_tts_service.generate_speech(
            text=text,
            voice_name=request.voice_name,
            language=request.language
        )
        # 在后台任务中清理旧文件
        background_tasks.add_task(gemini_tts_service.cleanup_old_files, 100)
        
        metadata = {
            "prompt_length": len(request.prompt),
            "response_length": len(text),
            "temperature": request.temperature,
            "voice_name": request.voice_name,
            "language": request.language or "auto",
            "tts_engine": "gemini"
        }
        
        filename = os.path.basename(audio_path)
        
        return CombinedResponse(
            success=True,
            text=text,
            audio_url=f"/audio/{filename}",
            filename=filename,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"生成文本并转语音错误: {str(e)}")
        return CombinedResponse(
            success=False,
            error=str(e)
        )

@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """获取音频文件"""
    try:
        audio_path = os.path.join(settings.AUDIO_OUTPUT_DIR, filename)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="音频文件不存在")
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=filename
        )
    except Exception as e:
        logger.error(f"获取音频文件错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=ApiStatusResponse)
async def get_api_status():
    """获取API状态"""
    try:
        status = await gemini_service.check_api_status()
        return ApiStatusResponse(**status)
    except Exception as e:
        logger.error(f"检查API状态错误: {str(e)}")
        return ApiStatusResponse(
            status="error",
            message=f"状态检查失败: {str(e)}"
        )

@router.post("/multi_speaker_tts", response_model=TextToSpeechResponse)
async def multi_speaker_tts(request: MultiSpeakerTTSRequest, background_tasks: BackgroundTasks):
    """多说话人文本转语音"""
    try:
        # 转换说话人配置格式
        speaker_configs = [
            {
                "speaker": config.speaker,
                "voice_name": config.voice_name
            }
            for config in request.speaker_configs
        ]
        
        audio_path = await gemini_tts_service.generate_multi_speaker_speech(
            text=request.text,
            speaker_configs=speaker_configs
        )
        
        # 获取文件名
        filename = os.path.basename(audio_path)
        
        # 在后台任务中清理旧文件
        background_tasks.add_task(gemini_tts_service.cleanup_old_files, 100)
        
        return TextToSpeechResponse(
            success=True,
            audio_url=f"/audio/{filename}",
            filename=filename,
            metadata={
                "text_length": len(request.text),
                "speaker_count": len(speaker_configs),
                "speakers": [config["speaker"] for config in speaker_configs],
                "tts_engine": "gemini"
            }
        )
    except Exception as e:
        logger.error(f"多说话人语音合成错误: {str(e)}")
        return TextToSpeechResponse(
            success=False,
            error=str(e)
        )

@router.get("/voices", response_model=VoicesResponse)
async def get_supported_voices():
    """获取Gemini TTS支持的声音列表"""
    try:
        voices = gemini_tts_service.get_supported_voices()
        return VoicesResponse(
            success=True,
            voices=voices
        )
    except Exception as e:
        logger.error(f"获取声音列表错误: {str(e)}")
        return VoicesResponse(
            success=False,
            error=str(e)
        )

@router.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages():
    """获取Gemini TTS支持的语言列表"""
    try:
        languages_list = gemini_tts_service.get_supported_languages()
        # 将语言列表转换为字典格式
        languages_dict = {lang: lang for lang in languages_list}
        return LanguagesResponse(
            success=True,
            languages=languages_dict
        )
    except Exception as e:
        logger.error(f"获取语言列表错误: {str(e)}")
        return LanguagesResponse(
            success=False,
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "Gemini Proxy",
        "version": "1.0.0"
    } 