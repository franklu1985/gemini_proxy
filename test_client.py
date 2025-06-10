#!/usr/bin/env python3
"""
Gemini 代理服务测试客户端
用于测试所有API接口的功能
"""

import requests
import json
import time
import os

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_AUDIO_DIR = "test_audio"

def ensure_test_dir():
    """确保测试目录存在"""
    if not os.path.exists(TEST_AUDIO_DIR):
        os.makedirs(TEST_AUDIO_DIR)

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def test_api_status():
    """测试API状态"""
    print("\n🔍 测试API状态...")
    try:
        print("发送状态请求...")
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        print(f"收到响应，状态码: {response.status_code}")
        result = response.json()
        print(f"状态: {result.get('status')}")
        print(f"消息: {result.get('message')}")
        if result.get('model'):
            print(f"模型: {result.get('model')}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("❌ API状态请求超时")
        return False
    except Exception as e:
        print(f"❌ API状态检查异常: {str(e)}")
        return False

def test_supported_languages():
    """测试获取支持的语言"""
    print("\n🔍 测试获取支持的语言...")
    try:
        response = requests.get(f"{BASE_URL}/languages")
        result = response.json()
        if result.get('success'):
            languages = result.get('languages', {})
            print(f"✅ 获取到 {len(languages)} 种支持的语言")
            # 显示前几种语言作为示例
            for i, (code, name) in enumerate(list(languages.items())[:5]):
                print(f"  {code}: {name}")
            if len(languages) > 5:
                print(f"  ... 还有 {len(languages) - 5} 种语言")
        else:
            print(f"❌ 获取语言失败: {result.get('error')}")
        return result.get('success', False)
    except Exception as e:
        print(f"❌ 获取语言异常: {str(e)}")
        return False

def test_text_generation():
    """测试文本生成"""
    print("\n🔍 测试文本生成...")
    try:
        payload = {
            "prompt": "请写一个关于春天的短诗，不超过50字",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(f"{BASE_URL}/generate", json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ 文本生成成功")
            print(f"生成的文本: {result.get('text')}")
            print(f"元数据: {result.get('metadata')}")
            return True, result.get('text')
        else:
            print(f"❌ 文本生成失败: {result.get('error')}")
            return False, None
    except Exception as e:
        print(f"❌ 文本生成异常: {str(e)}")
        return False, None

def test_text_to_speech(text=None):
    """测试Gemini TTS语音合成"""
    print("\n🔍 测试Gemini TTS语音合成...")
    try:
        test_text = text or "你好，这是Gemini原生TTS语音合成测试。欢迎使用新的语音功能！"
        
        payload = {
            "text": test_text,
            "voice_name": "Kore",
            "language": None  # 让模型自动检测
        }
        
        response = requests.post(f"{BASE_URL}/text_to_speech", json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ Gemini TTS 语音合成成功")
            print(f"音频文件: {result.get('filename')}")
            print(f"音频URL: {result.get('audio_url')}")
            print(f"元数据: {result.get('metadata')}")
            
            # 下载音频文件
            audio_url = f"http://localhost:8000{result.get('audio_url')}"
            return download_audio(audio_url, result.get('filename'))
        else:
            print(f"❌ Gemini TTS 语音合成失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Gemini TTS 语音合成异常: {str(e)}")
        return False

def test_multi_speaker_tts():
    """测试多说话人TTS"""
    print("\n🔍 测试多说话人TTS...")
    try:
        payload = {
            "text": "TTS 对话测试：Joe: 你好，Jane！今天天气真不错。Jane: 是的，很适合出去走走。",
            "speaker_configs": [
                {
                    "speaker": "Joe",
                    "voice_name": "Kore"
                },
                {
                    "speaker": "Jane",
                    "voice_name": "Puck"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/multi_speaker_tts", json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ 多说话人TTS成功")
            print(f"音频文件: {result.get('filename')}")
            print(f"音频URL: {result.get('audio_url')}")
            print(f"元数据: {result.get('metadata')}")
            
            # 下载音频文件
            audio_url = f"http://localhost:8000{result.get('audio_url')}"
            return download_audio(audio_url, result.get('filename'))
        else:
            print(f"❌ 多说话人TTS失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 多说话人TTS异常: {str(e)}")
        return False

def test_get_voices():
    """测试获取声音列表"""
    print("\n🔍 测试获取声音列表...")
    try:
        response = requests.get(f"{BASE_URL}/voices")
        result = response.json()
        
        if result.get('success'):
            voices = result.get('voices', [])
            print(f"✅ 获取到 {len(voices)} 种声音")
            print("支持的声音:")
            for voice in voices:
                print(f"  - {voice}")
        else:
            print(f"❌ 获取声音列表失败: {result.get('error')}")
        return result.get('success', False)
    except Exception as e:
        print(f"❌ 获取声音列表异常: {str(e)}")
        return False

def test_generate_and_speak():
    """测试生成文本并转语音（Gemini TTS）"""
    print("\n🔍 测试生成文本并转语音（Gemini TTS）...")
    try:
        payload = {
            "prompt": "简单介绍一下人工智能，不超过30字",
            "max_tokens": 80,
            "temperature": 0.6,
            "voice_name": "Puck",
            "language": None
        }
        
        response = requests.post(f"{BASE_URL}/generate_and_speak", json=payload)
        result = response.json()
        
        if result.get('success'):
            print("✅ 生成文本并转语音成功")
            print(f"生成的文本: {result.get('text')}")
            print(f"音频文件: {result.get('filename')}")
            print(f"元数据: {result.get('metadata')}")
            
            # 下载音频文件
            audio_url = f"http://localhost:8000{result.get('audio_url')}"
            return download_audio(audio_url, result.get('filename'))
        else:
            print(f"❌ 生成文本并转语音失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 生成文本并转语音异常: {str(e)}")
        return False

def test_history_generation():
    """测试基于历史的文本生成"""
    print("\n🔍 测试基于历史的文本生成...")
    import time
    
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮您的吗？"},
                {"role": "user", "content": "请简单介绍一下你自己"}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        # 添加重试机制处理SSL错误
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"发送历史生成请求... (尝试 {attempt + 1}/{max_retries})")
                response = requests.post(f"{BASE_URL}/generate_with_history", json=payload, timeout=60)
                result = response.json()
                break
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as conn_error:
                print(f"⚠️ 连接错误: {str(conn_error)}")
                if attempt < max_retries - 1:
                    print(f"等待 {2 * (attempt + 1)} 秒后重试...")
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    raise conn_error
            except Exception as e:
                if "ssl" in str(e).lower() or "unexpected_eof" in str(e).lower():
                    print(f"⚠️ SSL/网络错误: {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"等待 {2 * (attempt + 1)} 秒后重试...")
                        time.sleep(2 * (attempt + 1))
                        continue
                raise e
        
        if result.get('success'):
            print("✅ 基于历史的文本生成成功")
            print(f"生成的文本: {result.get('text')}")
            return True
        else:
            print(f"❌ 基于历史的文本生成失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 基于历史的文本生成异常: {str(e)}")
        return False

def download_audio(url, filename):
    """下载音频文件"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            ensure_test_dir()
            filepath = os.path.join(TEST_AUDIO_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ 音频文件已下载: {filepath}")
            return True
        else:
            print(f"❌ 下载音频文件失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载音频文件异常: {str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行 Gemini 代理服务测试")
    print("=" * 50)
    
    # 测试计数
    total_tests = 0
    passed_tests = 0
    
    # 健康检查
    total_tests += 1
    if test_health_check():
        passed_tests += 1
    
    # API状态检查
    total_tests += 1
    if test_api_status():
        passed_tests += 1
    
    # 获取支持的语言
    total_tests += 1
    if test_supported_languages():
        passed_tests += 1
    
    # 获取声音列表
    total_tests += 1
    if test_get_voices():
        passed_tests += 1
    
    # 文本生成
    total_tests += 1
    success, generated_text = test_text_generation()
    if success:
        passed_tests += 1
    
    # Gemini TTS 文本转语音
    total_tests += 1
    if test_text_to_speech(generated_text):
        passed_tests += 1
    
    # 多说话人TTS
    total_tests += 1
    if test_multi_speaker_tts():
        passed_tests += 1
    
    # 生成文本并转语音
    total_tests += 1
    if test_generate_and_speak():
        passed_tests += 1
    
    # 基于历史的文本生成
    total_tests += 1
    if test_history_generation():
        passed_tests += 1
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"📊 测试完成")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查服务配置")

if __name__ == "__main__":
    # 检查服务是否运行
    print("🔍 检查服务是否可用...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务不可用，请先启动服务: python main.py")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务，请确保服务正在运行")
        print("启动命令: python main.py")
        exit(1)
    
    print("✅ 服务可用，开始测试")
    run_all_tests() 