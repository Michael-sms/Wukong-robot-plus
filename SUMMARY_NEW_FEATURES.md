# wukong-robot 新增功能总结文档

本文档详细总结了项目近期新增的核心功能，包括实现思路、算法原理及预期效果。

## 1. VAD 静音检测 (Voice Activity Detection)

### 实现思路与原理
- **混合检测机制**: 采用了 **能量阈值 (Energy Threshold)** 与 **WebRTC VAD** 相结合的策略。
  - **能量检测**: 计算音频帧的均方根 (RMS) 能量，只有能量超过动态阈值（`energy_threshold`）时才视为潜在语音。
  - **WebRTC VAD**: 使用 `webrtcvad` 库基于高斯混合模型 (GMM) 对音频帧进行人声/非人声分类。
- **判定逻辑**: 只有当“能量检测”与“WebRTC VAD”同时判定为语音时，系统才认为检测到了有效语音。
- **相关文件**: `robot/VAD.py`

#### 伪代码
```python
def is_speech(frame):
    energy = rms(frame)
    is_vad = webrtcvad(frame)
    return (energy > energy_threshold) and is_vad
```

#### 关键参数
- **`sample_rate`**: 采样率，默认 16000 Hz
- **`frame_duration`**: 帧长度，默认 30ms
- **`level`**: WebRTC VAD 灵敏度等级（0-3），默认 3（最严格）
- **`energy_threshold`**: 能量阈值基准，默认 500，可根据环境噪音动态调整

### 预期效果
- **抗噪能力增强**: 在嘈杂环境下能有效过滤背景噪音，避免误唤醒或误录音。
- **精准截断**: 实现了“停顿即截”的效果，用户说话结束后机器人能更敏锐地停止录音，提升交互的流畅度和响应速度。

---

## 2. 声纹识别与用户注册

### 核心模型与原理
- **模型架构**: 使用 **ECAPA-TDNN** (基于 `speechbrain/spkrec-ecapa-voxceleb`) 深度神经网络模型。
- **特征提取**: 将任意长度的语音片段映射为 **192维** 的声纹特征向量 (Embedding)。
- **向量检索**: 集成 **Faiss** 向量数据库，使用余弦相似度 (Cosine Similarity) 进行高效的特征比对和 Top-1 用户检索。
- **相似度阈值**: 默认设置为 **0.25**，该阈值适用于 ECAPA-TDNN 模型。阈值范围建议：
  - **0.20-0.25**: 宽松，适合家庭环境，可能出现误识别
  - **0.25-0.30**: 平衡，推荐设置
  - **0.30-0.40**: 严格，适合安全要求高的场景
- **相关文件**: `robot/sdk/SpeakerID.py`

### 用户注册功能
- **实现思路**:
  1. **交互引导**: 插件引导用户语音输入名字、喜欢的动漫角色及角色定位（如“主人”、“朋友”）。
  2. **样本采集**: 录制一段较长的用户语音（约10-15秒），确保提取到稳定的声纹特征。
  3. **数据持久化**: 将提取的声纹向量存入内存中的 Faiss 索引，同时将用户画像（姓名、ID、偏好配置）存入 `static/user_db.json`。
- **预期效果**: 机器人能够“记住”用户的声音，并关联其个性化偏好，为后续的定制化交互打下基础。
- **相关文件**: `plugins/RegisterVoice.py`

#### 伪代码
```python
# 录音 -> 提取特征 -> Faiss 入库 -> 保存画像
audio = record(long_timeout)  # silent_threshold=300, timeout=15s
vector = ecapa_tdnn.encode(audio)  # 输出 (1, 192) 向量
faiss.normalize_L2(vector)  # L2归一化，用于余弦相似度计算
faiss_index.add(vector)  # 加入内存索引
user_db.append({id, name, context, embedding=vector})
save(user_db)  # 持久化到 static/user_db.json
```

#### 录音参数优化
- **`silent_threshold`**: 声纹采集时设为 **300**（高于普通对话的 150-200），给用户更多思考和说话时间
- **`recording_timeout`**: 最大录音时长 **15秒**，确保采集足够长的语音样本以提取稳定特征
- **推荐采集内容**: 让用户朗读一段完整的句子（如自我介绍），而非单个词语

### 声纹验证功能
- **实现思路**:
  1. 实时录制用户语音。
  2. 提取特征并在 Faiss 库中检索最相似的用户。
  3. 若相似度得分超过阈值（默认 0.25），则判定识别成功，加载该用户的上下文信息（如喜欢的角色语音）。
- **预期效果**: 用户无需自报家门，机器人即可识别“你是谁”，并自动切换到用户喜欢的角色音色进行回复。
- **相关文件**: `plugins/VerifyVoice.py`

#### 伪代码
```python
audio = record()
query = ecapa_tdnn.encode(audio)
faiss.normalize_L2(query)
score, idx = faiss_index.search(query, k=1)
if score > threshold:
    user = user_db[idx]
    apply_context(user.context)  # 切换角色语音等
else:
    report_unmatched(score)
```

---

## 3. 查看与删除已注册用户

### 查看用户
- **实现思路**: 读取并遍历用户数据库，通过 TTS 播报当前所有已注册用户的编号、姓名及其绑定的角色偏好。
- **预期效果**: 用户可通过语音指令“查看用户”快速了解系统中的注册名单。
- **相关文件**: `plugins/ListUsers.py`

### 删除用户
- **实现思路**:
  - **语音端**: 支持通过“删除X号用户”的指令，从内存列表和 JSON 数据库中移除指定用户，并触发 Faiss 索引的重建。
  - **工具端**: 提供了命令行工具，支持按编号、ID或姓名进行精确删除。
- **预期效果**: 提供了灵活的数据库维护手段，方便清理无效或错误的声纹数据。
- **相关文件**: `plugins/DeleteUser.py`

#### 伪代码（删除后重建索引）
```python
deleted = users.pop(target_idx)
# 重建索引步骤：
faiss_index.reset()  # 清空旧索引
if users:  # 如果还有剩余用户
    embeddings = [np.array(u['embedding']) for u in users]
    matrix = np.vstack(embeddings)  # 堆叠成矩阵 (N, 192)
    faiss.normalize_L2(matrix)  # L2归一化
    faiss_index.add(matrix)  # 批量添加
save(user_db)  # 同步到文件
```

#### 索引重建的必要性
删除用户后，Faiss 索引中的向量位置与 `user_db` 数组索引必须保持一致。由于 Faiss 不支持按索引删除单个向量，因此采用**全量重建**策略：清空索引后重新添加所有剩余用户的向量。

---

## 4. 角色语音功能

本模块实现了基于用户偏好的动态语音合成（TTS）切换，支持 **Edge-TTS**、**VITS**、**Bert-VITS2**、**GPT-SoVITS** 等多种引擎，其中 **GPT-SoVITS** 是目前效果最好的少样本语音克隆方案。

### 涉及文件与功能
1. **`robot/CharacterVoice.py` (核心配置)**
   - **功能**: 维护角色名到 TTS 配置（引擎类型、音色代码、服务端地址）的映射表。
   - **原理**: 提供 `get_character_voice` 接口，根据传入的角色名返回对应的语音合成参数。

2. **`plugins/TestCharacterVoice.py` (测试插件)**
   - **功能**: 允许用户通过语音指令测试当前生效的角色音色。
   - **预期效果**: 用户说出“测试语音”时，机器人会用当前配置的角色音色（如“千早爱音”）进行自我介绍，确认配置生效。

3. **`tools/character_voice_config.py` (配置工具)**
   - **功能**: 命令行交互工具 (CLI)。
   - **预期效果**: 
     - 列出所有可用的 Edge-TTS 音色（如“晓晓”、“云希”）。
     - 允许用户动态添加新的角色配置并进行语音合成测试，生成测试音频文件。

4. **`tools/user_manager.py` (用户管理工具)**
   - **功能**: 虽然主要用于用户数据库管理（增删改查），但它承载了**绑定用户与角色语音**的关键数据结构。
   - **预期效果**: 管理员可通过此工具查看每个用户绑定的 `fav_char` (喜欢角色)，从而验证角色语音功能的个性化数据基础。

#### 伪代码（角色语音选择）
```python
# 声纹识别后自动切换
user, score = speaker_id.identify(audio)
if user:
    fav_char = user['context'].get('fav_char')
    voice_cfg = CharacterVoice.get_character_voice(fav_char)
    
    if voice_cfg['engine'] == 'edge-tts':
        tts = EdgeTTS(voice=voice_cfg['voice'])
    elif voice_cfg['engine'] == 'vits':
        tts = VITS(server_url, speaker_id)
    elif voice_cfg['engine'] == 'gpt-sovits':
        tts = GPTSoVITS(
            ref_audio_path=voice_cfg['ref_audio_path'],
            prompt_text=voice_cfg['prompt_text'],
            prompt_lang=voice_cfg['prompt_lang']
        )
    
    current_user_context = user['context']  # 保存上下文
tts.speak(reply)
```

#### 动态切换机制
系统在 `Conversation.py` 中实现了 TTS 引擎的动态切换：
1. **声纹识别触发**: 当 `identify_speaker()` 成功识别用户后，自动调用 `switch_character_voice()`
2. **保存默认引擎**: 初始化时保存 `default_tts`，未识别到用户时可恢复默认语音
3. **支持多引擎**: 完整支持 Edge-TTS、GPT-SoVITS，VITS/Bert-VITS2 预留接口
4. **实时生效**: 切换后立即对当前会话的所有 TTS 输出生效

### TTS 引擎技术对比

| 引擎 | 优势 | 劣势 | 适用场景 | 样本需求 |
|------|------|------|---------|----------|
| **Edge-TTS** | 免费、稳定、无需部署 | 仅标准音色，不像真实角色 | 快速测试、低成本方案 | 无 |
| **VITS** | 音质好、可训练真实角色 | 需大量数据训练（>1小时音频） | 有充足语料的角色克隆 | 高（>1小时） |
| **Bert-VITS2** | 韵律自然、情感丰富 | 训练复杂、需GPU推理 | 高质量角色语音项目 | 高（>1小时） |
| **GPT-SoVITS** | **少样本克隆**（5-10秒）、音质接近真人 | 需独立部署服务 | **推荐方案**：快速克隆角色语音 | **极低（5-10秒）** |

### GPT-SoVITS 实现原理

#### 核心技术
- **模型架构**: 基于 GPT 的序列到序列语音合成模型，结合 SoVITS（Soft-VC VITS）技术
- **少样本学习**: 使用 **参考音频（5-10秒）** 作为 prompt，通过注意力机制捕捉说话人的音色特征
- **跨语言支持**: 支持中文、日文、英文的语音合成，且参考音频语言可与目标语言不同

#### 工作流程
```python
# 1. 服务端接收请求
request = {
    "ref_audio_path": "/path/to/reference.wav",  # 参考音频（5-10秒干声）
    "prompt_text": "参考音频对应的文字内容",      # 音频转录文本
    "prompt_lang": "ja",                         # 参考音频语言
    "text": "要合成的目标文本",                  # 待合成文本
    "text_lang": "zh"                            # 目标语言
}

# 2. 模型推理
ref_features = extract_speaker_embedding(ref_audio)  # 提取说话人特征
mel_spectrogram = gpt_model.generate(
    text=target_text,
    speaker_embedding=ref_features  # 注入说话人信息
)
audio_output = sovits_vocoder.decode(mel_spectrogram)  # 生成波形

# 3. 返回合成音频
return audio_output  # WAV格式
```

#### 配置示例
在 `robot/CharacterVoice.py` 中配置角色映射：
```python
CHARACTER_VOICE_MAP = {
    "千早爱音": {
        "engine": "gpt-sovits",
        # 参考音频路径（必须是GPT-SoVITS服务器可访问的路径）
        "ref_audio_path": "C:/Models/Audio/soyo_sample.wav",
        # 参考音频的文本内容（需准确对应）
        "prompt_text": "あー、りっきーは知らないか〜。私、作文得意なんだよね。",
        # 参考音频的语言
        "prompt_lang": "ja",
        # 要合成的目标语言
        "text_lang": "zh",
        "description": "千早爱音真实语音克隆"
    }
}
```

#### 关键参数说明
- **`ref_audio_path`**: 
  - 必须是 GPT-SoVITS 服务所在机器的**绝对路径**
  - 音频要求：干声（无背景音乐）、清晰、5-10秒
  - 支持格式：WAV、MP3
  
- **`prompt_text`**: 
  - 必须与参考音频内容**完全一致**（包括标点符号）
  - 用于模型对齐音素和音频
  
- **`prompt_lang` / `text_lang`**: 
  - 支持：`zh`（中文）、`ja`（日语）、`en`（英语）
  - 可以不同（如用日语参考音频合成中文）

#### 部署要求
```bash
# 1. 克隆并安装 GPT-SoVITS
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
pip install -r requirements.txt

# 2. 下载预训练模型（参考官方文档）
# 模型会自动下载到 GPT_SoVITS/pretrained_models/

# 3. 启动 API 服务
python api.py
# 默认监听 http://127.0.0.1:9880
```

#### 在 config.yml 中配置服务地址
```yaml
# 设置默认 TTS 引擎
tts_engine: gpt-sovits

# GPT-SoVITS 服务配置
gpt_sovits:
    server_url: "http://127.0.0.1:9880"  # 服务器地址
    ref_audio_path: "C:/path/to/reference.wav"
    prompt_text: "参考音频对应的文本"
    prompt_lang: "ja"
    text_lang: "zh"
```

---

## 5. 全链路时延检测

### 实现思路与原理
- **埋点追踪 (Tracing)**: 在语音交互的生命周期中（唤醒 -> ASR识别 -> NLU理解 -> 技能处理 -> TTS合成 -> 音频播放）植入时间戳埋点。
- **网络监控**: 
  - 实时计算 WebSocket 通信的 **RTT (往返时延)**。
  - 监控网络 **抖动 (Jitter)** 和 **丢包率**，评估网络稳定性。
- **阈值分析**: 对比各阶段耗时与预设阈值（如 ASR < 250ms），自动判定是否达标。

#### 各阶段延迟阈值配置
| 阶段 | 阈值 (ms) | 说明 |
|------|----------|------|
| 唤醒检测 (wakeup) | 500 | 从检测到唤醒词到开始录音 |
| ASR 识别 (asr) | 1500 | 语音转文字耗时（网络服务） |
| NLU 理解 (nlu) | 800 | 意图识别与槽位提取（网络服务） |
| 技能处理 (skill) | 3000 | 插件逻辑执行时间（含多次TTS调用） |
| TTS 合成 (tts) | 5000 | 文字转语音合成（Edge-TTS网络服务） |
| 音频播放 (play) | 500 | 音频输出延迟 |
| **总延迟 (total)** | **15000** | **端到端响应时间（15秒内合理）** |
| WebSocket延迟 (ws_latency) | 100 | 单次通信RTT |
| WebSocket抖动 (ws_jitter) | 50 | 连续延迟波动 |

> **注意**: 以上阈值是针对使用网络服务（腾讯云ASR、百度NLU、Edge-TTS等）的实际场景设定。如果您使用本地模型，可以将阈值调整得更严格。

#### 抖动计算公式
```python
jitter = avg(|latency[i] - latency[i-1]|)  # 连续延迟的平均差值
if jitter > 20ms:
    warn("网络抖动过大，可能导致断音")
```

#### 伪代码（单次会话追踪）
```python
tracker.mark('session_start')
...
tracker.mark('wakeup_detected')
tracker.mark('asr_start'); tracker.mark('asr_end')
tracker.mark('nlu_start'); tracker.mark('nlu_end')
tracker.mark('skill_start'); tracker.mark('skill_end')
tracker.mark('tts_start'); tracker.mark('tts_end')
tracker.mark('play_start'); tracker.mark('response_end')

for stage in stages:
    duration = tracker.calculate(stage)
    warn_if(duration > threshold[stage])
report = tracker.to_dict(); save(report)
```

### 预期效果
- **性能诊断**: 用户可通过“延迟报告”指令获取当前的系统性能分析，快速定位导致响应迟缓的环节（是网络卡顿还是模型推理慢）。
- **体验保障**: 结合抖动监控，确保在局域网环境下语音流的连续性，防止断音。

### 相关文件
- `robot/LatencyMonitor.py`: 监控核心逻辑与报告生成。
- `plugins/LatencyCheck.py`: 语音查询接口插件。
