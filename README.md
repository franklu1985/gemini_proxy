# Gemini 代理服务

一个基于 Google Gemini API 的代理服务，支持文本生成和高质量语音合成功能。

## ✨ 主要功能

- 🤖 **Gemini AI 文本生成** - 使用 gemini-1.5-flash 模型生成高质量文本
- 🎵 **Gemini 原生TTS** - 使用 gemini-2.5-flash-preview-tts 模型进行语音合成
- 🎭 **多说话人TTS** - 支持多说话人对话语音合成
- 🌍 **多语言支持** - 支持24种语言的语音合成
- 🎚️ **30种预制声音** - 不同风格和特色的声音选择
- 🔄 **组合服务** - 一键生成文本并转换为语音
- 📝 **对话历史** - 支持基于历史的文本生成
- 🌐 **RESTful API** - 完整的API接口

## 🚀 快速开始

### 生产环境部署（推荐）

#### 宝塔面板一键部署 ⭐

如果您使用Ubuntu系统 + 宝塔面板，推荐使用我们的一键部署方案：

```bash
# 一键部署脚本
bash bt_quick_install.sh

# 服务管理
./bt_service.sh start
./bt_service.sh status
./bt_service.sh logs
```

**优势**：
- 🚀 自动环境检测和配置
- 🎛️ 宝塔面板图形化管理
- 🌐 自动Nginx反向代理
- 📊 实时监控和日志
- 🔒 SSL证书自动申请

**详细指南**：[宝塔面板部署文档](bt_deploy.md)

#### 传统Linux部署

```bash
# 部署脚本
./deploy.sh

# 服务管理 
./service.sh start
```

**详细指南**：[生产环境部署文档](DEPLOYMENT.md)

### 开发环境

#### 1. 环境要求

- Python 3.8+
- Google Gemini API Key

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境

创建 `.env` 文件并设置 API 密钥：

```env
GEMINI_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```

#### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

#### 5. 测试服务

```bash
python test_client.py
```

## 📡 API 接口

### 文本生成

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "写一个关于春天的短诗",
       "max_tokens": 100,
       "temperature": 0.7
     }'
```

### Gemini TTS 语音合成

```bash
curl -X POST "http://localhost:8000/api/v1/text_to_speech" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "你好，这是Gemini TTS语音合成测试",
       "voice_name": "Kore",
       "language": "auto"
     }'
```

### 多说话人TTS

```bash
curl -X POST "http://localhost:8000/api/v1/multi_speaker_tts" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Joe: 你好，今天天气真不错！Jane: 是的，很适合出去走走。",
       "speaker_configs": [
         {"speaker": "Joe", "voice_name": "Kore"},
         {"speaker": "Jane", "voice_name": "Puck"}
       ]
     }'
```

### 生成文本并转语音

```bash
curl -X POST "http://localhost:8000/api/v1/generate_and_speak" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "简单介绍一下人工智能",
       "voice_name": "Zephyr",
       "max_tokens": 80
     }'
```

## 🎵 支持的声音

Gemini TTS 提供30种不同风格的预制声音：

**常用声音**：Zephyr、Puck、Charon、Kore、Fenrir、Leda、Orus、Aoede

**更多声音**：Callirrhoe、Autonoe、Enceladus、Iapetus、Umbriel、Algieba、Despina、Erinome、Algenib、Rasalgethi、Laomedeia、Achernar、Alnilam、Schedar、Gacrux、Pulcherrima、Achird、Zubenelgenubi、Vindemiatrix、Sadachbia、Sadaltager、Sulafat

## 🌍 支持的语言

支持24种语言：ar-EG、en-US、fr-FR、hi-IN、id-ID、it-IT、ja-JP、ko-KR、pt-BR、ru-RU、nl-NL、pl-PL、th-TH、tr-TR、vi-VN、ro-RO、uk-UA、bn-BD、en-IN、mr-IN、ta-IN、te-IN、de-DE、es-US

## 📖 API 文档

- **详细API文档**: [API_DOCS.md](./API_DOCS.md) - 完整的API接口文档
- **Swagger UI**: http://localhost:8000/docs - 交互式API文档
- **ReDoc**: http://localhost:8000/redoc - API文档备选视图

## 🧪 测试

运行测试客户端：

```bash
python test_client.py
```

测试包括：健康检查、API状态检查、文本生成、Gemini TTS语音合成、多说话人TTS、组合服务、语言和声音列表。

## 📁 项目结构

```
gemini_proxy/
├── main.py                   # 主应用文件
├── config.py                # 配置管理
├── requirements.txt         # 依赖列表
├── test_client.py           # 测试客户端
├── README.md               # 项目文档
├── API_DOCS.md            # 详细API接口文档
├── .gitignore             # Git忽略文件
├── api/
│   └── endpoints.py        # API路由定义
├── models/
│   └── requests.py         # 请求/响应模型
└── services/
    ├── gemini_service.py       # Gemini文本服务
    └── gemini_tts_service.py   # Gemini TTS服务
```

## �� 许可证

MIT License 