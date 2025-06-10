import google.genai as genai
from typing import Optional, Dict, Any, List
from config import settings
import logging
import asyncio
import os
import hashlib
import base64
import wave

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiTTSService:
    """Gemini 原生 TTS 服务 - 使用新的 google-genai API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash-preview-tts"
        self.output_dir = settings.AUDIO_OUTPUT_DIR
        self.client = None
        
        if self.api_key:
            self._initialize_client()
        else:
            logger.warning("Gemini API Key 未配置")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _initialize_client(self):
        """初始化 Gemini 客户端"""
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini TTS 客户端初始化成功，使用模型: {self.model_name}")
        except Exception as e:
            logger.error(f"Gemini TTS 客户端初始化失败: {str(e)}")
            self.client = None
            # 不要抛出异常，允许服务启动但返回错误信息
    
    def _generate_filename(self, text: str, voice_name: str, language: str = None) -> str:
        """根据文本内容生成唯一的文件名"""
        content = f"{text}_{voice_name}_{language or 'auto'}"
        hash_object = hashlib.md5(content.encode())
        return f"gemini_{hash_object.hexdigest()}.wav"
    
    async def generate_speech(
        self, 
        text: str, 
        voice_name: str = "Kore",
        language: Optional[str] = None,
        slow: bool = False
    ) -> str:
        """
        使用 Gemini TTS 生成语音文件
        
        Args:
            text: 要转换的文本
            voice_name: 声音名称 (默认: Kore)
            language: 语言代码 (可选，模型会自动检测)
            slow: 是否使用慢速语音（暂不支持）
            
        Returns:
            生成的音频文件路径
        """
        if not self.client:
            raise Exception("Gemini TTS 客户端未初始化，请检查 API Key 配置")
        
        try:
            if not text.strip():
                raise ValueError("文本内容不能为空")
            
            # 生成文件名
            filename = self._generate_filename(text, voice_name, language)
            filepath = os.path.join(self.output_dir, filename)
            
            # 如果文件已存在，直接返回路径
            if os.path.exists(filepath):
                logger.info(f"使用缓存的音频文件: {filename}")
                return filepath
            
            # 在线程池中执行 TTS 操作，添加超时保护
            loop = asyncio.get_event_loop()
            audio_data = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    self._generate_audio, 
                    text, voice_name
                ),
                timeout=30.0  # 30秒超时
            )
            
            # 保存音频文件
            self._save_pcm_as_wav(audio_data, filepath)
            
            logger.info(f"成功生成音频文件: {filename}")
            return filepath
            
        except asyncio.TimeoutError:
            logger.error("Gemini TTS 请求超时（30秒）")
            raise Exception("Gemini TTS 请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"Gemini TTS 语音合成失败: {str(e)}")
            raise Exception(f"Gemini TTS 语音合成失败: {str(e)}")
    
    def _generate_audio(self, text: str, voice_name: str) -> bytes:
        """在线程中生成音频"""
        try:
            # 验证输入参数
            if not text or not text.strip():
                raise ValueError("文本内容不能为空")
            
            if voice_name not in self.get_supported_voices():
                logger.warning(f"声音 {voice_name} 可能不受支持，将尝试使用")
            
            logger.info(f"开始生成语音: {text[:50]}... (声音: {voice_name})")
            
            # 使用统一的单说话人音频生成方法
            return self._generate_single_speaker_audio(text, voice_name)
            
        except Exception as e:
            logger.error(f"Gemini TTS API 错误: {str(e)}")
            raise e
    
    async def generate_multi_speaker_speech(
        self,
        text: str,
        speaker_configs: List[Dict[str, str]]
    ) -> str:
        """
        生成多说话人语音
        
        Args:
            text: 包含说话人标记的文本
            speaker_configs: 说话人配置列表，格式: [{"speaker": "Joe", "voice_name": "Kore"}]
            
        Returns:
            生成的音频文件路径
        """
        if not self.client:
            raise Exception("Gemini TTS 客户端未初始化，请检查 API Key 配置")
        
        try:
            if not text.strip():
                raise ValueError("文本内容不能为空")
            
            # 生成文件名
            speakers_str = "_".join([f"{config['speaker']}_{config['voice_name']}" for config in speaker_configs])
            filename = self._generate_filename(text, speakers_str)
            filepath = os.path.join(self.output_dir, filename)
            
            # 如果文件已存在，直接返回路径
            if os.path.exists(filepath):
                logger.info(f"使用缓存的多说话人音频文件: {filename}")
                return filepath
            
            # 在线程池中执行多说话人 TTS 操作，添加超时保护
            loop = asyncio.get_event_loop()
            audio_data = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    self._generate_multi_speaker_audio, 
                    text, speaker_configs
                ),
                timeout=30.0  # 30秒超时
            )
            
            # 保存音频文件
            self._save_pcm_as_wav(audio_data, filepath)
            
            logger.info(f"成功生成多说话人音频文件: {filename}")
            return filepath
            
        except asyncio.TimeoutError:
            logger.error("Gemini TTS 多说话人请求超时（30秒）")
            raise Exception("Gemini TTS 多说话人请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"Gemini TTS 多说话人语音合成失败: {str(e)}")
            raise Exception(f"Gemini TTS 多说话人语音合成失败: {str(e)}")
    
    def _generate_multi_speaker_audio(self, text: str, speaker_configs: List[Dict[str, str]]) -> bytes:
        """在线程中生成多说话人音频"""
        try:
            # 使用新版本 google-genai 的多说话人TTS功能
            from google.genai.types import (
                GenerateContentConfig, SpeechConfig, MultiSpeakerVoiceConfig, 
                SpeakerVoiceConfig, VoiceConfig, PrebuiltVoiceConfig
            )
            
            logger.info(f"开始生成多说话人语音: {text[:50]}... (说话人数: {len(speaker_configs)})")
            
            # 构建说话人配置
            speaker_voice_configs = []
            for config in speaker_configs:
                speaker_voice_config = SpeakerVoiceConfig(
                    speaker=config["speaker"],
                    voice_config=VoiceConfig(
                        prebuilt_voice_config=PrebuiltVoiceConfig(
                            voice_name=config["voice_name"]
                        )
                    )
                )
                speaker_voice_configs.append(speaker_voice_config)
                logger.info(f"配置说话人: {config['speaker']} -> 声音: {config['voice_name']}")
            
            # 构建多说话人配置
            config = GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=SpeechConfig(
                    multi_speaker_voice_config=MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_voice_configs
                    )
                )
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=text,
                config=config
            )
            
            # 验证响应
            if not response:
                raise Exception("Gemini API 返回空响应")
            
            # 检查是否有直接的音频数据
            if hasattr(response, 'audio') and response.audio:
                try:
                    if hasattr(response.audio, 'data'):
                        # 如果音频数据是直接的bytes
                        if isinstance(response.audio.data, bytes):
                            logger.info(f"获取到多说话人音频数据，大小: {len(response.audio.data)} 字节")
                            return response.audio.data
                        # 如果音频数据是base64字符串
                        elif isinstance(response.audio.data, str):
                            audio_data = base64.b64decode(response.audio.data)
                            logger.info(f"解码base64多说话人音频数据，大小: {len(audio_data)} 字节")
                            return audio_data
                except Exception as e:
                    logger.error(f"处理直接多说话人音频数据失败: {str(e)}")
            
            # 检查candidates结构
            if not response.candidates or len(response.candidates) == 0:
                raise Exception("Gemini API 未返回候选结果")
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise Exception("响应中缺少内容部分")
            
            # 遍历所有parts寻找音频数据
            for part in candidate.content.parts:
                # 检查不同的可能属性名
                for attr_name in ['inline_data', 'inlineData', 'data', 'audio_data', 'audioData']:
                    if hasattr(part, attr_name):
                        attr_value = getattr(part, attr_name)
                        
                        if attr_value:
                            # 如果是对象，检查其data属性
                            if hasattr(attr_value, 'data') and attr_value.data:
                                try:
                                    if isinstance(attr_value.data, bytes):
                                        logger.info(f"获取到多说话人音频数据，大小: {len(attr_value.data)} 字节")
                                        return attr_value.data
                                    elif isinstance(attr_value.data, str):
                                        audio_data = base64.b64decode(attr_value.data)
                                        logger.info(f"解码base64多说话人音频数据，大小: {len(audio_data)} 字节")
                                        return audio_data
                                except Exception as decode_error:
                                    logger.error(f"解码多说话人音频数据失败: {str(decode_error)}")
                            
                            # 如果直接是bytes或字符串
                            elif isinstance(attr_value, bytes):
                                logger.info(f"获取到多说话人音频数据，大小: {len(attr_value)} 字节")
                                return attr_value
                            elif isinstance(attr_value, str):
                                try:
                                    audio_data = base64.b64decode(attr_value)
                                    logger.info(f"解码base64多说话人音频数据，大小: {len(audio_data)} 字节")
                                    return audio_data
                                except Exception as decode_error:
                                    logger.error(f"解码多说话人音频数据失败: {str(decode_error)}")
                
                # 检查part本身是否直接包含音频数据
                if hasattr(part, 'data') and part.data:
                    try:
                        if isinstance(part.data, bytes):
                            logger.info(f"获取到多说话人音频数据，大小: {len(part.data)} 字节")
                            return part.data
                        elif isinstance(part.data, str):
                            audio_data = base64.b64decode(part.data)
                            logger.info(f"解码base64多说话人音频数据，大小: {len(audio_data)} 字节")
                            return audio_data
                    except Exception as decode_error:
                        logger.error(f"解码多说话人音频数据失败: {str(decode_error)}")
            
            # 如果都没找到，抛出详细错误
            error_msg = "多说话人响应中未找到音频数据"
            if response.candidates and response.candidates[0].content:
                error_msg += f"，Parts数量: {len(response.candidates[0].content.parts)}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Gemini TTS 多说话人 API 错误: {str(e)}")
            raise e
    
    def _generate_single_speaker_audio(self, text: str, voice_name: str) -> bytes:
        """生成单说话人音频的内部方法"""
        from google.genai.types import GenerateContentConfig, SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
        
        config = GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            )
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=text,
            config=config
        )
        
        # 验证响应
        if not response:
            raise Exception("Gemini API 返回空响应")
        
        # 检查是否有直接的音频数据
        if hasattr(response, 'audio') and response.audio:
            try:
                if hasattr(response.audio, 'data'):
                    # 如果音频数据是直接的bytes
                    if isinstance(response.audio.data, bytes):
                        logger.info(f"获取到音频数据，大小: {len(response.audio.data)} 字节")
                        return response.audio.data
                    # 如果音频数据是base64字符串
                    elif isinstance(response.audio.data, str):
                        audio_data = base64.b64decode(response.audio.data)
                        logger.info(f"解码base64音频数据，大小: {len(audio_data)} 字节")
                        return audio_data
            except Exception as e:
                logger.error(f"处理直接音频数据失败: {str(e)}")
        
        # 检查candidates结构
        if not response.candidates or len(response.candidates) == 0:
            raise Exception("Gemini API 未返回候选结果")
        
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise Exception("响应中缺少内容部分")
        
        # 遍历所有parts寻找音频数据
        for part in candidate.content.parts:
            # 检查不同的可能属性名
            for attr_name in ['inline_data', 'inlineData', 'data', 'audio_data', 'audioData']:
                if hasattr(part, attr_name):
                    attr_value = getattr(part, attr_name)
                    
                    if attr_value:
                        # 如果是对象，检查其data属性
                        if hasattr(attr_value, 'data') and attr_value.data:
                            try:
                                if isinstance(attr_value.data, bytes):
                                    logger.info(f"获取到音频数据，大小: {len(attr_value.data)} 字节")
                                    return attr_value.data
                                elif isinstance(attr_value.data, str):
                                    audio_data = base64.b64decode(attr_value.data)
                                    logger.info(f"解码base64音频数据，大小: {len(audio_data)} 字节")
                                    return audio_data
                            except Exception as decode_error:
                                logger.error(f"解码音频数据失败: {str(decode_error)}")
                        
                        # 如果直接是bytes或字符串
                        elif isinstance(attr_value, bytes):
                            logger.info(f"获取到音频数据，大小: {len(attr_value)} 字节")
                            return attr_value
                        elif isinstance(attr_value, str):
                            try:
                                audio_data = base64.b64decode(attr_value)
                                logger.info(f"解码base64音频数据，大小: {len(audio_data)} 字节")
                                return audio_data
                            except Exception as decode_error:
                                logger.error(f"解码音频数据失败: {str(decode_error)}")
            
            # 检查part本身是否直接包含音频数据
            if hasattr(part, 'data') and part.data:
                try:
                    if isinstance(part.data, bytes):
                        logger.info(f"获取到音频数据，大小: {len(part.data)} 字节")
                        return part.data
                    elif isinstance(part.data, str):
                        audio_data = base64.b64decode(part.data)
                        logger.info(f"解码base64音频数据，大小: {len(audio_data)} 字节")
                        return audio_data
                except Exception as decode_error:
                    logger.error(f"解码音频数据失败: {str(decode_error)}")
        
        # 如果都没找到，抛出详细错误
        error_msg = "响应中未找到音频数据"
        if response.candidates and response.candidates[0].content:
            error_msg += f"，Parts数量: {len(response.candidates[0].content.parts)}"
        
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def get_supported_voices(self) -> List[str]:
        """获取支持的声音列表"""
        return [
            "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda",
            "Orus", "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus",
            "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalgethi",
            "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima",
            "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
        ]
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return [
            "ar-EG", "en-US", "fr-FR", "hi-IN", "id-ID", "it-IT",
            "ja-JP", "ko-KR", "pt-BR", "ru-RU", "nl-NL", "pl-PL",
            "th-TH", "tr-TR", "vi-VN", "ro-RO", "uk-UA", "bn-BD",
            "en-IN", "mr-IN", "ta-IN", "te-IN", "de-DE", "es-US"
        ]
    
    def cleanup_old_files(self, max_files: int = 100):
        """清理旧的音频文件，保留最新的指定数量文件"""
        try:
            files = []
            for filename in os.listdir(self.output_dir):
                if filename.startswith('gemini_') and filename.endswith('.wav'):
                    filepath = os.path.join(self.output_dir, filename)
                    files.append((filepath, os.path.getctime(filepath)))
            
            # 按创建时间排序
            files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除超出限制的文件
            if len(files) > max_files:
                for filepath, _ in files[max_files:]:
                    try:
                        os.remove(filepath)
                        logger.info(f"删除旧文件: {filepath}")
                    except Exception as e:
                        logger.warning(f"删除文件失败 {filepath}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"清理文件失败: {str(e)}")

    def _save_pcm_as_wav(self, pcm_data: bytes, wav_file: str):
        """将PCM数据保存为WAV文件"""
        try:
            # 根据Gemini API文档，音频输出为24kHz, 16-bit, mono
            sample_rate = 24000
            sample_width = 2  # 16-bit = 2 bytes
            channels = 1  # mono
            
            with wave.open(wav_file, 'wb') as wav_f:
                wav_f.setnchannels(channels)
                wav_f.setsampwidth(sample_width)
                wav_f.setframerate(sample_rate)
                wav_f.writeframes(pcm_data)
            
            logger.info(f"成功保存PCM数据为WAV文件: {wav_file}, 大小: {len(pcm_data)} 字节")
        except Exception as e:
            logger.error(f"保存PCM数据为WAV文件失败: {str(e)}")
            raise e

# 创建全局实例
gemini_tts_service = GeminiTTSService() 