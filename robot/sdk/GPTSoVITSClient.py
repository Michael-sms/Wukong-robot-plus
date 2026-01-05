# coding: utf-8
# !/usr/bin/env python3

"""
GPT-SoVITS TTS API Client
GPT-SoVITS 项目地址：https://github.com/RVC-Boss/GPT-SoVITS
"""

import requests
from robot import logging

logger = logging.getLogger(__name__)


def tts(
    text,
    server_url,
    text_lang="zh",
    ref_audio_path=None,
    prompt_text=None,
    prompt_lang="zh",
    aux_ref_audio_paths=None,
    top_k=5,
    top_p=1.0,
    temperature=1.0,
    text_split_method="cut5",
    batch_size=1,
    speed_factor=1.0,
    seed=-1,
    parallel_infer=True,
    repetition_penalty=1.35,
    timeout=30
):
    """
    调用 GPT-SoVITS API 进行语音合成
    
    Args:
        text: 要合成的文本
        server_url: GPT-SoVITS 服务器地址，如 http://127.0.0.1:9880
        refer_wav_path: 参考音频路径（可选，用于零样本克隆）
        prompt_text: 参考音频对应的文本（可选）
        prompt_language: 参考音频语言，默认 "zh"（中文）
        text_language: 合成文本语言，默认 "zh"
        cut_punc: 文本切分的标点符号，默认中英文标点
        top_k: top_k 采样参数，默认 15
        top_p: top_p 采样参数，默认 1.0
        temperature: 温度参数，控制随机性，默认 1.0
        speed: 语速，默认 1.0
        timeout: 请求超时时间（秒），默认 30
    
    Returns:
        bytes: 音频数据（WAV 格式）
        
    Raises:
        requests.exceptions.RequestException: 请求失败时抛出
    """
    
    # 构建请求参数（JSON body 格式）
    payload = {
        "text": text,
        "text_lang": text_lang,
        "prompt_lang": prompt_lang,
        "top_k": top_k,
        "top_p": top_p,
        "temperature": temperature,
        "text_split_method": text_split_method,
        "batch_size": batch_size,
        "speed_factor": speed_factor,
        "seed": seed,
        "parallel_infer": parallel_infer,
        "repetition_penalty": repetition_penalty
    }
    
    # 如果提供了参考音频，添加相关参数
    if ref_audio_path:
        payload["ref_audio_path"] = ref_audio_path
        if prompt_text:
            payload["prompt_text"] = prompt_text
        logger.info(f"使用参考音频进行克隆: {ref_audio_path}")
    else:
        logger.info("使用服务端默认音色（未提供参考音频）")
    
    # 如果有辅助参考音频
    if aux_ref_audio_paths:
        payload["aux_ref_audio_paths"] = aux_ref_audio_paths
    
    # 去除尾部斜杠
    server_url = server_url.rstrip("/")
    
    # 发送 POST 请求（JSON body 格式）
    logger.info(f"GPT-SoVITS TTS 请求: {server_url}/tts")
    logger.info(f"  文本: {text[:50]}{'...' if len(text) > 50 else ''}")
    logger.info(f"  参数: text_lang={text_lang}, 参考音频={'已提供' if ref_audio_path else '未提供'}")
    
    try:
        # 使用 json 参数发送 JSON body
        response = requests.post(
            f"{server_url}/tts",
            json=payload,  # JSON body 格式
            timeout=timeout,
            stream=True
        )
        
        logger.info(f"GPT-SoVITS 响应状态码: {response.status_code}")
        
        # 检查响应状态
        if response.status_code != 200:
            error_text = response.text[:1000] if response.text else "无错误信息"
            logger.error(f"GPT-SoVITS 服务器返回错误（{response.status_code}）: {error_text}")
            logger.error(f"请求的完整 payload: {payload}")
            response.raise_for_status()
        
        # 收集音频数据
        audio_data = b""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                audio_data += chunk
        
        if len(audio_data) == 0:
            logger.error("GPT-SoVITS 返回的音频数据为空")
            raise ValueError("音频数据为空")
        
        logger.info(f"GPT-SoVITS TTS 成功，音频大小: {len(audio_data)} bytes")
        return audio_data
        
    except requests.exceptions.Timeout:
        logger.error(f"GPT-SoVITS TTS 请求超时（超过 {timeout} 秒）")
        logger.error(f"  请检查服务器 {server_url} 是否响应缓慢")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"GPT-SoVITS TTS 连接失败: {server_url}")
        logger.error(f"  错误详情: {str(e)}")
        logger.error(f"  请检查：")
        logger.error(f"    1. 服务器是否启动")
        logger.error(f"    2. IP 地址是否正确")
        logger.error(f"    3. 端口是否正确")
        logger.error(f"    4. 防火墙是否阻止连接")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"GPT-SoVITS TTS HTTP 错误: {e}")
        logger.error(f"  响应状态码: {response.status_code if 'response' in locals() else '未知'}")
        raise
    except Exception as e:
        logger.error(f"GPT-SoVITS TTS 未知错误: {type(e).__name__}: {str(e)}")
        raise
