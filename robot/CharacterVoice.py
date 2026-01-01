# -*- coding: utf-8 -*-
"""
角色语音配置文件
将动漫角色映射到对应的语音合成配置
"""

# 角色语音映射表
# 支持多种TTS引擎：edge-tts, vits, bert-vits2, gpt-sovits
CHARACTER_VOICE_MAP = {
    # 示例：使用 edge-tts 的音色模拟角色
    "千早爱音": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoxiaoNeural",  # 温柔女声
        "description": "温柔可爱的少女音"
    },
    # "明日香": {
    #    "engine": "edge-tts", 
    #   "voice": "zh-CN-XiaoyiNeural",  # 活泼女声
    #    "description": "活泼傲娇的少女音"
    # },
    # "绫波丽": {
    #     "engine": "edge-tts",
    #     "voice": "zh-CN-XiaomengNeural",  # 平静女声
    #     "description": "平静温和的少女音"
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
}

# 默认语音配置（当角色未配置或未识别到用户时使用）
DEFAULT_VOICE = {
    "engine": "edge-tts",
    "voice": "zh-CN-XiaoxiaoNeural"
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
    return EDGE_TTS_VOICES.get(name, DEFAULT_VOICE["voice"])
