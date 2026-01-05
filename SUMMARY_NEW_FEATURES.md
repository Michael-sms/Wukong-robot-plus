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

### 预期效果
- **抗噪能力增强**: 在嘈杂环境下能有效过滤背景噪音，避免误唤醒或误录音。
- **精准截断**: 实现了“停顿即截”的效果，用户说话结束后机器人能更敏锐地停止录音，提升交互的流畅度和响应速度。

---

## 2. 声纹识别与用户注册

### 核心模型与原理
- **模型架构**: 使用 **ECAPA-TDNN** (基于 `speechbrain/spkrec-ecapa-voxceleb`) 深度神经网络模型。
- **特征提取**: 将任意长度的语音片段映射为 **192维** 的声纹特征向量 (Embedding)。
- **向量检索**: 集成 **Faiss** 向量数据库，使用余弦相似度 (Cosine Similarity) 进行高效的特征比对和 Top-1 用户检索。
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
audio = record(long_timeout)
vector = ecapa_tdnn.encode(audio)
faiss.normalize_L2(vector)
faiss_index.add(vector)
user_db.append({id, name, context, embedding=vector})
save(user_db)
```

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
matrix = np.vstack([u.embedding for u in users])
faiss_index.reset()
faiss.normalize_L2(matrix)
faiss_index.add(matrix)
save(user_db)
```

---

## 4. 角色语音功能

本模块实现了基于用户偏好的动态语音合成（TTS）切换，支持 Edge-TTS 等多种引擎。

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
fav_char = current_user.context.get("fav_char")
voice_cfg = CharacterVoice.get_character_voice(fav_char)
tts.switch(voice_cfg)
tts.speak(reply)
```

---

## 5. 全链路时延检测

### 实现思路与原理
- **埋点追踪 (Tracing)**: 在语音交互的生命周期中（唤醒 -> ASR识别 -> NLU理解 -> 技能处理 -> TTS合成 -> 音频播放）植入时间戳埋点。
- **网络监控**: 
  - 实时计算 WebSocket 通信的 **RTT (往返时延)**。
  - 监控网络 **抖动 (Jitter)** 和 **丢包率**，评估网络稳定性。
- **阈值分析**: 对比各阶段耗时与预设阈值（如 ASR < 250ms），自动判定是否达标。

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
