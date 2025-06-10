# Gemini 代理服务 API 文档

## 📖 概述

Gemini 代理服务提供基于 Google Gemini API 的文本生成和语音合成功能。本文档详细描述了所有可用的 REST API 端点。

**基础URL**: `http://localhost:8000/api/v1`

## 🔐 认证

本服务目前不需要额外认证，Gemini API Key 在服务端配置。

## 📡 API 端点

### 1. 健康检查

#### `GET /health`

检查服务健康状态。

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 2. API 状态检查

#### `GET /status`

检查 Gemini API 连接状态。

**响应模型**: `ApiStatusResponse`

**响应示例**:
```json
{
  "status": "success",
  "message": "Gemini API 连接正常",
  "model": "gemini-1.5-flash"
}
```

**错误响应示例**:
```json
{
  "status": "error",
  "message": "API密钥验证失败"
}
```

---

### 3. 文本生成

#### `POST /generate`

使用 Gemini 模型生成文本。

**请求模型**: `TextGenerationRequest`

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `prompt` | string | ✅ | - | 输入提示文本 (1-10000字符) |
| `max_tokens` | integer | ❌ | null | 最大token数 (1-4000) |
| `temperature` | float | ❌ | 0.7 | 创造性参数 (0.0-1.0) |
| `top_p` | float | ❌ | 0.9 | 核心采样参数 (0.0-1.0) |

**请求示例**:
```json
{
  "prompt": "请介绍一下人工智能的发展历史",
  "max_tokens": 1000,
  "temperature": 0.8,
  "top_p": 0.9
}
```

**响应模型**: `TextGenerationResponse`

**成功响应示例**:
```json
{
  "success": true,
  "text": "人工智能（AI）的发展历史可以追溯到20世纪40年代...",
  "metadata": {
    "prompt_length": 15,
    "response_length": 500,
    "temperature": 0.8,
    "top_p": 0.9
  }
}
```

**错误响应示例**:
```json
{
  "success": false,
  "error": "输入文本过长"
}
```

---

### 4. 基于历史的文本生成

#### `POST /generate_with_history`

基于对话历史生成文本。

**请求模型**: `TextGenerationWithHistoryRequest`

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `messages` | array | ✅ | - | 对话历史消息列表 |
| `max_tokens` | integer | ❌ | null | 最大token数 (1-4000) |
| `temperature` | float | ❌ | 0.7 | 创造性参数 (0.0-1.0) |

**消息格式**:
```json
{
  "role": "user|assistant",
  "content": "消息内容"
}
```

**请求示例**:
```json
{
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！我是AI助手，有什么可以帮助你的吗？"},
    {"role": "user", "content": "请介绍一下机器学习"}
  ],
  "temperature": 0.8
}
```

**响应模型**: `TextGenerationResponse`

---

### 5. 文本转语音

#### `POST /text_to_speech`

将文本转换为语音（使用 Gemini TTS）。

**请求模型**: `TextToSpeechRequest`

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `text` | string | ✅ | - | 要转换的文本 (1-5000字符) |
| `voice_name` | string | ❌ | "Kore" | 声音名称 |
| `language` | string | ❌ | null | 语言代码（自动检测） |

**请求示例**:
```json
{
  "text": "你好，欢迎使用Gemini语音合成服务！",
  "voice_name": "Puck",
  "language": "zh"
}
```

**响应模型**: `TextToSpeechResponse`

**成功响应示例**:
```json
{
  "success": true,
  "audio_url": "/audio/gemini_abc123.wav",
  "filename": "gemini_abc123.wav",
  "metadata": {
    "text_length": 18,
    "voice_name": "Puck",
    "language": "zh",
    "tts_engine": "gemini"
  }
}
```

---

### 6. 多说话人语音合成

#### `POST /multi_speaker_tts`

生成多说话人对话语音。

**请求模型**: `MultiSpeakerTTSRequest`

**请求参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `text` | string | ✅ | 包含说话人标记的文本 |
| `speaker_configs` | array | ✅ | 说话人配置列表 |

**说话人配置格式**:
```json
{
  "speaker": "说话人名称",
  "voice_name": "声音名称"
}
```

**请求示例**:
```json
{
  "text": "Alice: 你好，今天天气怎么样？\nBob: 今天天气很好，阳光明媚。",
  "speaker_configs": [
    {"speaker": "Alice", "voice_name": "Kore"},
    {"speaker": "Bob", "voice_name": "Puck"}
  ]
}
```

**响应模型**: `TextToSpeechResponse`

---

### 7. 生成文本并转语音

#### `POST /generate_and_speak`

一步完成文本生成和语音合成。

**请求模型**: `CombinedRequest`

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `prompt` | string | ✅ | - | 输入提示文本 |
| `max_tokens` | integer | ❌ | null | 最大token数 |
| `temperature` | float | ❌ | 0.7 | 创造性参数 |
| `voice_name` | string | ❌ | "Kore" | 声音名称 |
| `language` | string | ❌ | null | 语音语言代码 |

**请求示例**:
```json
{
  "prompt": "请简单介绍一下量子计算",
  "temperature": 0.8,
  "voice_name": "Zephyr"
}
```

**响应模型**: `CombinedResponse`

**成功响应示例**:
```json
{
  "success": true,
  "text": "量子计算是一种基于量子力学原理的计算方式...",
  "audio_url": "/audio/gemini_def456.wav",
  "filename": "gemini_def456.wav",
  "metadata": {
    "prompt_length": 10,
    "response_length": 200,
    "temperature": 0.8,
    "voice_name": "Zephyr",
    "language": "auto",
    "tts_engine": "gemini"
  }
}
```

---

### 8. 获取音频文件

#### `GET /audio/{filename}`

下载生成的音频文件。

**路径参数**:
- `filename`: 音频文件名

**响应**: 音频文件（WAV格式）

**示例**:
```
GET /audio/gemini_abc123.wav
```

---

### 9. 获取支持的声音列表

#### `GET /voices`

获取所有可用的预制声音。

**响应模型**: `VoicesResponse`

**成功响应示例**:
```json
{
  "success": true,
  "voices": [
    "Kore", "Puck", "Zephyr", "Aria", "Aurora", "Atlas", 
    "Boreas", "Cosmos", "Echo", "Ember", "Ethos", "Felix",
    "Genesis", "Grove", "Haven", "Horizon", "Lyra", "Nova",
    "Odyssey", "Orion", "Perseus", "Quasar", "Rhythm", "Sage",
    "Serenity", "Spark", "Stellar", "Tempest", "Vox", "Zen"
  ]
}
```

---

### 10. 获取支持的语言列表

#### `GET /languages`

获取所有支持的语言代码。

**响应模型**: `LanguagesResponse`

**成功响应示例**:
```json
{
  "success": true,
  "languages": {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "ru": "Русский",
    "ar": "العربية",
    "hi": "हिन्दी",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia",
    "ms": "Bahasa Melayu",
    "tr": "Türkçe",
    "pl": "Polski",
    "nl": "Nederlands",
    "sv": "Svenska",
    "da": "Dansk",
    "no": "Norsk",
    "fi": "Suomi",
    "hu": "Magyar"
  }
}
```

---

## 🎵 声音特色

### 可用声音列表及特色

| 声音名称 | 特色描述 |
|----------|----------|
| **Kore** | 温暖、友好、平易近人 |
| **Puck** | 活泼、年轻、精力充沛 |
| **Zephyr** | 平静、舒缓、专业 |
| **Aria** | 优雅、音乐感、表现力强 |
| **Aurora** | 清新、明亮、充满希望 |
| **Atlas** | 稳重、权威、可信赖 |
| **Boreas** | 深沉、有力、威严 |
| **Cosmos** | 神秘、广阔、富有想象力 |
| **Echo** | 清晰、回响、技术感 |
| **Ember** | 温暖、亲密、情感丰富 |

*更多声音请使用 `/voices` 端点获取完整列表*

---

## ❌ 错误代码

### HTTP 状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 业务错误码

所有API响应都包含 `success` 字段，当为 `false` 时，`error` 字段包含错误信息。

**常见错误**:
- `"输入文本过长"` - 文本超过最大长度限制
- `"API密钥验证失败"` - Gemini API Key 无效
- `"模型响应为空"` - Gemini API 返回空响应
- `"音频文件不存在"` - 请求的音频文件不存在
- `"不支持的声音名称"` - 指定的声音不在支持列表中

---

## 📚 使用示例

### Python 客户端示例

```python
import requests

# 基础配置
BASE_URL = "http://localhost:8000/api/v1"

# 1. 文本生成
def generate_text(prompt):
    response = requests.post(f"{BASE_URL}/generate", json={
        "prompt": prompt,
        "temperature": 0.8
    })
    return response.json()

# 2. 文本转语音
def text_to_speech(text, voice="Kore"):
    response = requests.post(f"{BASE_URL}/text_to_speech", json={
        "text": text,
        "voice_name": voice
    })
    return response.json()

# 3. 生成文本并转语音
def generate_and_speak(prompt, voice="Puck"):
    response = requests.post(f"{BASE_URL}/generate_and_speak", json={
        "prompt": prompt,
        "voice_name": voice,
        "temperature": 0.7
    })
    return response.json()

# 使用示例
result = generate_and_speak("介绍一下深度学习", "Zephyr")
if result["success"]:
    print(f"生成的文本: {result['text']}")
    print(f"音频URL: {result['audio_url']}")
```

### cURL 示例

```bash
# 文本生成
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "解释什么是机器学习",
    "temperature": 0.8
  }'

# 文本转语音
curl -X POST "http://localhost:8000/api/v1/text_to_speech" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个语音合成测试",
    "voice_name": "Kore"
  }'

# 获取声音列表
curl "http://localhost:8000/api/v1/voices"

# 健康检查
curl "http://localhost:8000/api/v1/health"
```

---

## 🔧 技术规格

- **音频格式**: WAV (24kHz, 16-bit, 单声道)
- **文本编码**: UTF-8
- **最大文本长度**: 5000字符 (TTS), 10000字符 (文本生成)
- **最大Token数**: 4000
- **支持语言**: 24种
- **可用声音**: 30种预制声音

---

## 📞 支持

如有问题或建议，请参考项目的 README.md 文件或提交 Issue。 