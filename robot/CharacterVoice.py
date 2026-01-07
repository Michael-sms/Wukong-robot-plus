# -*- coding: utf-8 -*-
"""
角色语音配置文件
将动漫角色映射到对应的语音合成配置
"""

# 角色语音映射表
# 支持多种TTS引擎：edge-tts, vits, bert-vits2, gpt-sovits
CHARACTER_VOICE_MAP = {
    # 示例：使用 edge-tts 的音色模拟角色
    "默认": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoxiaoNeural",  # 温柔女声
        "description": "温柔可爱的少女音"
    },
    
    # "莉莉丝": {
    #     "engine": "edge-tts",   
    #     "voice": "zh-CN-XiaoyiNeural",  # 活泼女声
    #     "description": "活泼开朗的少女音"
    # },
    # VITS 模型示例（需要部署 VITS 服务）
    # "千早爱音": {
    #     "engine": "vits",
    #     "server_url": "http://127.0.0.1:7860",
    #     "speaker_id": 0,  # 角色对应的 speaker ID
    #     "description": "VITS训练的千早爱音语音"
    # },
    
    # Bert-VITS2 示例
    # "宵宫": {
    #     "engine": "bert-vits2",
    #     "server_url": "http://127.0.0.1:5000",
    #     "speaker_id": "yoimiya",
    #     "description": "Bert-VITS2 宵宫语音"
    # },

    # GPT-SoVITS 示例（局域网服务器）
    # 重要：ref_audio_path 必须是服务器端的文件路径，不是本地路径
    "千早爱音": {
        "engine": "gpt-sovits",
        "server_url": "http://192.168.1.103:9880",  # 您的服务器IP
        # 参考音频路径（服务器端的路径）
        "ref_audio_path": "C:/Users/Usotsuki_Kaze/Desktop/MyGO!!!!!/千早愛音/あー、りっきーは知らないか〜。私、作文得意なんだよね。今回も高評価だったし.mp3",
        "prompt_text": "あー、りっきーは知らないか〜。私、作文得意なんだよね。今回も高評価だったし",
        "prompt_lang": "ja",      # 参考音频语言：日语
        "text_lang": "zh",        # 合成文本语言：中文（可改为 ja 合成日语）
        "description": "GPT-SoVITS 千早爱音语音（日语音色克隆）"
    },
}

# 默认语音配置（当角色未配置或未识别到用户时使用）
DEFAULT_VOICE = {
    # "engine": "gpt-sovits",
    # "server_url": "http://192.168.1.103:9880",
    # "ref_audio_path": "C:/Users/Usotsuki_Kaze/Desktop/MyGO!!!!!/千早愛音/あー、りっきーは知らないか〜。私、作文得意なんだよね。今回も高評価だったし.mp3",
    # "prompt_text": "あー、りっきーは知らないか〜。私、作文得意なんだよね。今回も高評価だったし",
    # "prompt_lang": "ja",
    # "text_lang": "zh"
    "engine": "edge-tts",
    "voice": "zh-CN-XiaoxiaoNeural",  # 温柔女声
}

# Edge-TTS 推荐音色列表（供用户选择）
EDGE_TTS_VOICES = {
    # 女声
    "晓晓": "zh-CN-XiaoxiaoNeural",      # 温柔女声
    "晓伊": "zh-CN-XiaoyiNeural",        # 活泼女声
    "晓梦": "zh-CN-XiaomengNeural",      # 平静女声
    "晓墨": "zh-CN-XiaomoNeural",        # 成熟女声
    "晓秋": "zh-CN-XiaoqiuNeural",       # 知性女声
    "晓睿": "zh-CN-XiaoruiNeural",       # 可爱女声
    "晓双": "zh-CN-XiaoshuangNeural",    # 少女音
    "晓萱": "zh-CN-XiaoxuanNeural",      # 温柔女声
    "晓颜": "zh-CN-XiaoyanNeural",       # 活泼女声
    "晓悠": "zh-CN-XiaoyouNeural",       # 温和女声
    "晓甄": "zh-CN-XiaozhenNeural",      # 成熟女声
    
    # 男声
    "云扬": "zh-CN-YunyangNeural",       # 新闻男声
    "云枫": "zh-CN-YunfengNeural",       # 成熟男声
    "云皓": "zh-CN-YunhaoNeural",        # 活力男声
    "云希": "zh-CN-YunxiNeural",         # 温和男声
    "云野": "zh-CN-YunyeNeural",         # 活泼男声
    "云泽": "zh-CN-YunzeNeural",         # 稳重男声
}


def get_character_voice(character_name):
    """
    根据角色名获取语音配置
    :param character_name: 角色名
    :return: 语音配置字典
    """
    if character_name and character_name in CHARACTER_VOICE_MAP:
        return CHARACTER_VOICE_MAP[character_name]
    return DEFAULT_VOICE


def add_character_voice(character_name, engine, **kwargs):
    """
    动态添加角色语音配置
    :param character_name: 角色名
    :param engine: TTS引擎 (edge-tts, vits, bert-vits2等)
    :param kwargs: 其他配置参数
    """
    CHARACTER_VOICE_MAP[character_name] = {
        "engine": engine,
        **kwargs
    }


def list_available_characters():
    """列出所有已配置的角色"""
    return list(CHARACTER_VOICE_MAP.keys())


def get_edge_voice_by_name(name):
    """根据中文名获取Edge-TTS音色代码"""
    # 修复：只在 DEFAULT_VOICE 是 edge-tts 引擎时才返回 voice
    if name in EDGE_TTS_VOICES:
        return EDGE_TTS_VOICES[name]
    # 如果 DEFAULT_VOICE 是 edge-tts 且有 voice 键
    if DEFAULT_VOICE.get("engine") == "edge-tts" and "voice" in DEFAULT_VOICE:
        return DEFAULT_VOICE["voice"]
    # 否则返回一个默认的 edge-tts 音色
    return "zh-CN-XiaoxiaoNeural"
