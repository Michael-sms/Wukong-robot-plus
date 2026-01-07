# 角色语音配置指南

## 概述

该功能允许你为不同的注册用户设置专属的角色语音。当系统通过声纹识别到用户后，会自动切换到该用户喜欢的角色语音进行TTS合成。

## 快速开始

### 1. 基础配置（使用 Edge-TTS）

Edge-TTS 是微软提供的免费TTS服务，虽然不是真正的动漫角色语音，但可以选择不同音色来模拟角色风格。

编辑 `robot/CharacterVoice.py` 中的 `CHARACTER_VOICE_MAP`：

```python
CHARACTER_VOICE_MAP = {
    "千早爱音": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoxiaoNeural",  # 温柔女声
        "description": "温柔可爱的少女音"
    },
    "明日香": {
        "engine": "edge-tts", 
        "voice": "zh-CN-XiaoyiNeural",  # 活泼女声
        "description": "活泼傲娇的少女音"
    },
}
```

#### 可用的 Edge-TTS 音色：

**女声：**
- `zh-CN-XiaoxiaoNeural` - 晓晓（温柔）
- `zh-CN-XiaoyiNeural` - 晓伊（活泼）
- `zh-CN-XiaomengNeural` - 晓梦（平静）
- `zh-CN-XiaomoNeural` - 晓墨（成熟）
- `zh-CN-XiaoruiNeural` - 晓睿（可爱）
- `zh-CN-XiaoshuangNeural` - 晓双（少女）

**男声：**
- `zh-CN-YunxiNeural` - 云希（温和）
- `zh-CN-YunyeNeural` - 云野（活泼）
- `zh-CN-YunfengNeural` - 云枫（成熟）

**查看所有音色：**
```bash
edge-tts --list-voices | grep zh-CN
```

### 2. 使用流程

1. **注册用户时选择喜欢的角色**
   - 对机器人说：`"注册声纹"`
   - 输入名字和喜欢的角色（如"千早爱音"）

2. **自动识别并切换语音**
   - 当你说话时，系统识别你的声纹
   - 自动切换到千早爱音对应的语音
   - 机器人回复时使用该语音

3. **验证是否生效**
   - 对机器人说：`"你好"`
   - 听到的语音应该是设置的角色音色

## 高级配置

### 方案1: 使用 VITS 模型（推荐）

VITS 可以训练真正的角色语音，效果最接近原角色。

#### 步骤：

1. **部署 VITS 服务**
```bash
# 克隆 VITS 项目
git clone https://github.com/jaywalnut310/vits.git
cd vits

# 安装依赖
pip install -r requirements.txt

# 使用预训练模型或训练自己的模型
# 启动推理服务（需要自己编写或使用现成的API服务）
python inference_server.py --port 7860
```

2. **修改 CharacterVoice.py 配置**
```python
"千早爱音": {
    "engine": "vits",
    "server_url": "http://127.0.0.1:7860",
    "speaker_id": 0,  # 如果是多说话人模型，指定speaker ID
    "description": "VITS训练的千早爱音语音"
}
```

3. **实现 VITS TTS 类**（在 `robot/TTS.py` 中添加）
```python
class VITS(AbstractTTS):
    """
    VITS TTS 引擎
    """
    SLUG = "vits"

    def __init__(self, server_url, speaker_id=0, **args):
        super(self.__class__, self).__init__()
        self.server_url = server_url
        self.speaker_id = speaker_id

    def get_speech(self, phrase):
        try:
            # 调用 VITS API
            response = requests.post(
                f"{self.server_url}/synthesize",
                json={
                    "text": phrase,
                    "speaker_id": self.speaker_id
                }
            )
            
            if response.status_code == 200:
                tmpfile = os.path.join(constants.TEMP_PATH, uuid.uuid4().hex + ".wav")
                with open(tmpfile, 'wb') as f:
                    f.write(response.content)
                logger.info(f"VITS 语音合成成功")
                return tmpfile
            else:
                logger.error(f"VITS 合成失败: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"VITS 合成出错: {e}")
            return None
```

### 方案2: 使用 Bert-VITS2（高质量）

Bert-VITS2 是改进版的VITS，支持更好的韵律和情感表达。

**参考项目：**
- https://github.com/fishaudio/Bert-VITS2
- https://github.com/PlayVoice/vits_chinese

### 方案3: 使用 GPT-SoVITS（少样本克隆/推荐）

GPT-SoVITS 是目前效果最好的少样本语音克隆方案，只需要 5-10 秒的参考音频，就能合成非常真实的语音。

#### 1. 部署 GPT-SoVITS 服务

需要单独部署 GPT-SoVITS 推理服务：

```bash
# 1. 克隆项目
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# 2. 安装依赖
pip install -r requirements.txt

# 3. 下载预训练模型（参考官方文档）

# 4. 启动 API 服务
python api.py
# 服务默认运行在 http://127.0.0.1:9880
```

#### 2. 准备参考音频

你需要准备一段角色的干声（无背景音乐）作为参考音频：
- **格式**：MP3/WAV
- **时长**：5-10 秒最佳
- **内容**：语音清晰，情感丰富
- **路径**：必须是 **GPT-SoVITS 服务所在机器** 的绝对路径

#### 3. 配置 CharacterVoice.py

```python
"这里填角色名": {
    "engine": "gpt-sovits",
    "ref_audio_path": "C:\\Models\\Audio\\sample.wav",  # 参考音频绝对路径
    "prompt_text": "这里是参考音频对应的文字内容",      # 参考音频的文本
    "prompt_lang": "zh",                                # 参考音频语言 (zh/ja/en)
    "text_lang": "zh",                                  # 合成目标语言
    "description": "GPT-SoVITS 语音克隆"
}
```

### 方案4: 使用在线角色语音API

一些平台提供动漫角色语音API：
- Moegoe（需要自己部署）
- 一些付费的角色语音服务

## 配置示例

### 完整配置示例（CharacterVoice.py）

```python
CHARACTER_VOICE_MAP = {
    # Edge-TTS 配置（免费，但不是真角色音）
    "千早爱音": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoxiaoNeural",
        "description": "温柔的少女音"
    },
    
    # VITS 配置（需要自己训练或找预训练模型）
    "宵宫": {
        "engine": "vits",
        "server_url": "http://127.0.0.1:7860",
        "speaker_id": 0,
        "description": "VITS训练的宵宫语音"
    },
    
    # Bert-VITS2 配置
    "派蒙": {
        "engine": "bert-vits2",
        "server_url": "http://127.0.0.1:5000",
        "speaker_id": "paimon",
        "description": "Bert-VITS2 派蒙语音"
    },

    # GPT-SoVITS 配置（推荐）
    "千早爱音(真)": {
        "engine": "gpt-sovits",
        # 必须是运行 GPT-SoVITS 服务的机器上的绝对路径
        "ref_audio_path": "D:/Models/GPT-SoVITS/ref_waves/soyo_01.wav",
        "prompt_text": "あー、りっきーは知らないか〜。私、作文得意なんだよね。",
        "prompt_lang": "ja",
        "description": "GPT-SoVITS 语音克隆"
    }
}
```

## 常见问题

### Q: Edge-TTS 的音色听起来不像角色怎么办？
A: Edge-TTS 只是标准的合成音，无法完全模拟角色。要真正的角色音需要使用 VITS、Bert-VITS2 等模型训练。

### Q: 如何获取角色语音数据训练模型？
A: 
1. 从动漫、游戏中提取角色语音
2. 使用音频处理工具清洗数据
3. 使用 VITS 或 Bert-VITS2 训练
4. 注意版权问题，仅供个人学习使用

### Q: 能否直接使用已训练好的模型？
A: 网上有一些开源的角色语音模型，但需要自己搭建推理服务。搜索关键词：
- "VITS 原神角色"
- "Bert-VITS2 动漫角色"
- "角色语音合成模型"

### Q: VITS 服务如何部署？
A: 参考项目 README，通常步骤：
1. 安装依赖（PyTorch, librosa等）
2. 下载预训练模型
3. 编写推理脚本
4. 启动 Flask/FastAPI 服务
5. 配置到 wukong-robot

## 推荐资源

### 开源项目
- **VITS**: https://github.com/jaywalnut310/vits
- **Bert-VITS2**: https://github.com/fishaudio/Bert-VITS2
- **GPT-SoVITS**: https://github.com/RVC-Boss/GPT-SoVITS
- **MoeGoe**: https://github.com/CjangCjengh/MoeGoe

### 预训练模型
- HuggingFace 上搜索 "vits" + "chinese"
- ModelScope 上的中文语音模型
- B站、GitHub 上分享的角色模型

### 教程
- VITS 训练教程: https://www.bilibili.com/（搜索"VITS训练"）
- Bert-VITS2 整合包: https://github.com/（搜索相关整合包）

## 注意事项

1. **版权问题**: 角色语音涉及版权，仅供个人学习使用
2. **计算资源**: VITS 推理需要一定的计算资源，建议有GPU
3. **音质**: Edge-TTS 音质稳定但不像角色；自训练模型效果取决于数据质量
4. **延迟**: 本地推理延迟低；在线API可能有网络延迟

## 未来扩展

- [ ] 支持情感标签（开心、难过、生气等）
- [ ] 支持多种音色混合
- [ ] 根据对话内容自动调整语气
- [ ] 支持实时语音克隆
