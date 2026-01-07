# 角色语音功能使用说明

## 🎯 功能概述

该功能实现了基于声纹识别的**个性化角色语音**回复。当系统识别到注册用户时，会自动切换到该用户喜欢的动漫角色语音进行TTS合成。

## ✨ 主要特性

- ✅ 声纹识别自动切换语音
- ✅ 支持多种TTS引擎（Edge-TTS、VITS、Bert-VITS2、GPT-SoVITS等）
- ✅ 灵活的角色配置系统
- ✅ 语音测试和管理工具
- ✅ 支持少样本语音克隆（GPT-SoVITS）

## 📁 新增文件

```
robot/
  ├── CharacterVoice.py          # 角色语音配置模块
  └── Conversation.py             # 修改：添加动态TTS切换

plugins/
  ├── TestCharacterVoice.py      # 测试角色语音插件
  ├── DeleteUser.py              # 删除用户插件
  ├── ListUsers.py               # 查看用户列表插件
  └── VerifyVoice.py             # 验证声纹插件

tools/
  ├── character_voice_config.py  # 角色语音配置工具
  └── user_manager.py            # 用户管理工具

docs/
  └── CHARACTER_VOICE_GUIDE.md   # 详细配置指南
```

## 🚀 快速开始

### 1. 配置角色语音

编辑 `robot/CharacterVoice.py`，添加角色配置：

```python
CHARACTER_VOICE_MAP = {
    "千早爱音": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoxiaoNeural",  # 温柔女声
        "description": "温柔可爱的少女音"
    },
    "你的角色名": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoyiNeural",   # 活泼女声
        "description": "活泼开朗的少女音"
    },
}
```

### 2. 注册用户并选择角色

对机器人说：`"注册声纹"`

按提示输入：
1. 你的名字
2. 喜欢的角色（如"千早爱音"）
3. 称呼方式（如"master"）
4. 录制声纹样本

### 3. 验证功能

**方式1：直接对话**
- 说话时系统自动识别声纹
- 机器人回复使用角色语音

**方式2：测试命令**
对机器人说：`"测试语音"` 或 `"当前语音"`

**方式3：验证声纹**
对机器人说：`"验证声纹"` 或 `"识别我"`

## 🛠️ 配置工具使用

### 角色语音配置工具

```bash
cd /home/yubanxian/wukong-robot
python tools/character_voice_config.py
```

**功能菜单：**
1. 查看可用的 Edge-TTS 音色
2. 查看当前角色配置
3. 添加新角色（Edge-TTS）
4. 测试角色语音
5. 退出

### 用户管理工具

```bash
cd /home/yubanxian/wukong-robot
python tools/user_manager.py
```

**功能菜单：**
1. 查看所有用户 - 显示所有已注册用户的详细信息
2. 删除用户（按编号） - 按列表编号快速删除
3. 删除用户（按ID） - 根据用户ID精确删除
4. 删除用户（按姓名） - 删除指定姓名的所有用户
5. 保存并退出 - 保存更改到数据库
6. 退出不保存 - 放弃所有更改

**使用示例：**

```bash
# 查看所有已注册用户
python tools/user_manager.py
# 选择 1 查看用户列表

# 删除某个用户
python tools/user_manager.py
# 选择 2 按编号删除
# 或选择 3 按ID删除
# 或选择 4 按姓名删除

# 记得选择 5 保存更改！
```

**用户信息显示格式：**
```
编号: 1
  姓名: 老三
  用户ID: user_1767019647
  喜欢角色: 千早爱音
  角色定位: master
```

### 查看可用音色

```bash
# 查看所有 Edge-TTS 音色
edge-tts --list-voices | grep zh-CN
```

## 🎨 推荐音色配置

### GPT-SoVITS 角色语音（推荐）

GPT-SoVITS 支持使用少量样本克隆真实角色语音，音质和相似度最高。

| 特点 | 说明 |
|-----|-----|
| 样本需求 | 仅需 5-10 秒参考音频 |
| 音质 | 接近真实角色声音 |
| 多语言 | 支持中文、日语、英语 |
| 部署 | 需要独立部署服务 |

### Edge-TTS 音色（免费易用）

Edge-TTS 是微软提供的免费 TTS 服务，虽然不是真正的角色音，但配置简单。

### 女性角色

| 角色风格 | 推荐音色 | 音色代码 |
|---------|---------|---------|
| 温柔可爱 | 晓晓 | zh-CN-XiaoxiaoNeural |
| 活泼开朗 | 晓伊 | zh-CN-XiaoyiNeural |
| 平静温和 | 晓梦 | zh-CN-XiaomengNeural |
| 可爱萝莉 | 晓睿 | zh-CN-XiaoruiNeural |
| 少女清纯 | 晓双 | zh-CN-XiaoshuangNeural |
| 成熟知性 | 晓墨 | zh-CN-XiaomoNeural |

### 男性角色

| 角色风格 | 推荐音色 | 音色代码 |
|---------|---------|---------|
| 温和友善 | 云希 | zh-CN-YunxiNeural |
| 活泼阳光 | 云野 | zh-CN-YunyeNeural |
| 成熟稳重 | 云枫 | zh-CN-YunfengNeural |
| 新闻播报 | 云扬 | zh-CN-YunyangNeural |

## 📝 使用示例

### 示例1：千早爱音配置

```python
"千早爱音": {
    "engine": "edge-tts",
    "voice": "zh-CN-XiaoxiaoNeural",  # 温柔音色
    "description": "LoveLive 千早爱音"
}
```

**使用流程：**
1. 注册时选择"千早爱音"
2. 系统识别到你时自动切换
3. 机器人使用温柔音色回复

### 示例2：多用户不同角色

```python
CHARACTER_VOICE_MAP = {
    "千早爱音": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    "明日香": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaoyiNeural"  # 活泼音色
    },
    "绫波丽": {
        "engine": "edge-tts",
        "voice": "zh-CN-XiaomengNeural"  # 平静音色
    }
}
```

用户A注册选择"千早爱音" → 听到温柔音  
用户B注册选择"明日香" → 听到活泼音  
用户C注册选择"绫波丽" → 听到平静音

## 🔧 高级配置

### 使用 GPT-SoVITS 克隆角色语音（推荐）

GPT-SoVITS 只需要少量音频样本（5-10秒）就能克隆真实的角色声音，是最接近原角色的方案。

#### 1. 部署 GPT-SoVITS 服务

```bash
# 克隆项目
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS

# 安装依赖
pip install -r requirements.txt

# 启动推理服务（默认端口 9880）
python api.py
```

#### 2. 准备参考音频

从角色语音中提取一段清晰的音频（5-10秒），并记录对应的文本内容。

**示例：**
- 音频文件：`千早爱音_sample.mp3`
- 对应文本：`あー、りっきーは知らないか〜。私、作文得意なんだよね。`

#### 3. 配置 config.yml

编辑 `~/.wukong/config.yml`：

```yaml
# 设置默认 TTS 引擎为 GPT-SoVITS
tts_engine: gpt-sovits

# GPT-SoVITS 配置
gpt_sovits:
    server_url: "http://127.0.0.1:9880"  # GPT-SoVITS 服务器地址
    # 参考音频路径（服务器端路径）
    ref_audio_path: "C:/path/to/千早爱音_sample.mp3"
    # 参考音频对应的文本
    prompt_text: "あー、りっきーは知らないか〜。私、作文得意なんだよね。"
    # 参考音频的语言（zh: 中文, ja: 日语, en: 英语）
    prompt_lang: "ja"
    # 要合成的文本语言
    text_lang: "zh"
    # 可选参数
    top_k: 5
    top_p: 1.0
    temperature: 1.0
```

#### 4. 配置角色语音映射

编辑 `robot/CharacterVoice.py`：

```python
CHARACTER_VOICE_MAP = {
    "千早爱音": {
        "engine": "gpt-sovits",
        "ref_audio_path": "C:/path/to/千早爱音_sample.mp3",
        "prompt_text": "あー、りっきーは知らないか〜。私、作文得意なんだよね。",
        "prompt_lang": "ja",
        "text_lang": "zh",
        "description": "千早爱音真实语音克隆"
    },
}
```

#### 5. 测试效果

```bash
# 注册声纹时选择"千早爱音"
# 对机器人说："注册声纹"

# 测试语音效果
# 对机器人说："测试语音"
```

### 使用 VITS 真角色语音

如果你有 VITS 训练的角色模型：

```python
"宵宫": {
    "engine": "vits",
    "server_url": "http://127.0.0.1:7860",
    "speaker_id": 0,
    "description": "原神 宵宫"
}
```

详细配置请查看：[docs/CHARACTER_VOICE_GUIDE.md](docs/CHARACTER_VOICE_GUIDE.md)

## 📋 管理命令

### 语音交互管理

**查看已注册用户**

对机器人说：`"查看用户"` 或 `"用户列表"`

**删除用户**

对机器人说：`"删除用户"`

按提示选择要删除的用户编号

**测试角色语音**

对机器人说：`"测试语音"` 或 `"当前语音"`

### 命令行管理工具

**用户管理工具（推荐）**

适合批量管理、精确删除、查看详细信息：

```bash
# 启动用户管理工具
python tools/user_manager.py

# 功能特点：
# - 显示完整用户信息（编号、ID、姓名、喜欢角色、角色定位）
# - 支持按编号、ID、姓名三种方式删除
# - 删除前预览，保存前确认
# - 可撤销操作（选择退出不保存）
```

**角色语音配置工具**

适合配置和测试角色语音：

```bash
# 启动角色配置工具
python tools/character_voice_config.py

# 功能特点：
# - 查看所有可用 Edge-TTS 音色
# - 添加新角色配置
# - 测试角色语音效果
# - 查看当前配置
```

**直接编辑数据库（高级）**

如果需要精确控制，可直接编辑：

```bash
# 编辑用户数据库
nano static/user_db.json

# 或使用 vim
vim static/user_db.json
```

**数据库结构：**
```json
[
  {
    "id": "user_1767019647",
    "name": "老三",
    "context": {
      "fav_char": "千早爱音",
      "role": "master"
    },
    "embedding": [0.123, 0.456, ...]
  }
]
```

## 🐛 常见问题

### Q1: 为什么声纹识别后语音没有切换？

**检查清单：**
1. ✅ 角色名是否在 `CHARACTER_VOICE_MAP` 中配置
2. ✅ 注册时输入的角色名是否完全匹配
3. ✅ 查看日志是否有切换成功的提示
4. ✅ 使用"测试语音"命令验证

**日志关键信息：**
```
[成员2] 已锁定用户: 老三, 偏好角色: 千早爱音
尝试切换到角色 '千早爱音' 的语音，引擎: edge-tts
已切换到 Edge-TTS 语音: zh-CN-XiaoxiaoNeural (角色: 千早爱音)
```

### Q2: 如何修改已注册用户的喜欢角色？

**方法1：** 重新注册（会生成新ID）  
**方法2：** 直接编辑 `static/user_db.json`

```json
{
  "id": "user_1767019647",
  "name": "老三",
  "context": {
    "fav_char": "千早爱音",  // 修改这里
    "role": "master"
  },
  "embedding": [...]
}
```

### Q3: Edge-TTS 音色不像角色怎么办？

Edge-TTS 是标准合成音，无法完全模拟角色。要真正的角色音需要：

1. **使用 GPT-SoVITS**（推荐）少样本克隆，仅需 5-10 秒音频
2. **使用 VITS** 训练角色模型（需要大量数据和训练时间）
3. **使用 Bert-VITS2** 高质量合成（需要训练）

参考：[docs/CHARACTER_VOICE_GUIDE.md](docs/CHARACTER_VOICE_GUIDE.md)

### Q6: GPT-SoVITS 如何获取参考音频？

**方法1：从动漫/游戏中提取**
```bash
# 使用 ffmpeg 提取音频
ffmpeg -i video.mp4 -ss 00:01:30 -t 10 -acodec copy output.mp3
```

**方法2：使用 UVR 分离人声**
- 下载 Ultimate Vocal Remover (UVR)
- 分离背景音乐，只保留人声
- 选择清晰的 5-10 秒片段

**注意事项：**
- 音频要清晰，无背景噪音
- 避免音乐和音效干扰
- 尽量选择情绪平稳的语音
- 记录准确的对应文本

### Q7: GPT-SoVITS 支持多个角色吗？

支持！为每个角色配置不同的参考音频：

```python
CHARACTER_VOICE_MAP = {
    "千早爱音": {
        "engine": "gpt-sovits",
        "ref_audio_path": "/path/to/千早爱音.mp3",
        "prompt_text": "参考文本1",
        "prompt_lang": "ja"
    },
    "明日香": {
        "engine": "gpt-sovits",
        "ref_audio_path": "/path/to/明日香.mp3",
        "prompt_text": "参考文本2",
        "prompt_lang": "ja"
    },
}
```

### Q4: 如何查看当前使用的音色？

```bash
# 查看日志
tail -f wukong.log | grep "切换到"

# 或使用测试命令
# 对机器人说："测试语音"
```

### Q5: 多用户时如何管理？

**语音交互方式：**
```bash
# 查看所有用户
# 对机器人说："查看用户"

# 删除不需要的用户
# 对机器人说："删除用户"
```

**命令行工具方式（推荐）：**
```bash
# 使用用户管理工具
python tools/user_manager.py

# 优势：
# 1. 可以看到完整的用户信息
# 2. 支持多种删除方式（编号/ID/姓名）
# 3. 批量操作更方便
# 4. 删除前可以预览
```

**快速操作示例：**
```bash
# 场景1：删除测试用户
python tools/user_manager.py
# 选择 1 查看列表 → 选择 2 按编号删除 → 输入编号 → 选择 5 保存

# 场景2：删除所有名为"测试"的用户
python tools/user_manager.py
# 选择 4 按姓名删除 → 输入"测试" → 选择 5 保存

# 场景3：只是查看不修改
python tools/user_manager.py
# 选择 1 查看列表 → 选择 6 退出不保存
```

## 📖 技术细节

### 工作流程

```
1. 用户说话 → 录音
   ↓
2. 声纹识别 → 匹配用户
   ↓
3. 获取用户喜欢的角色
   ↓
4. 切换对应TTS引擎/音色
   ↓
5. 机器人回复使用角色语音
```

### 代码逻辑

```python
# Conversation.py
def identify_speaker(self, audio_fp):
    user, score = self.speaker_id.identify(audio_data)
    if user:
        fav_char = user['context'].get('fav_char')
        self.switch_character_voice(fav_char)  # 切换语音

def switch_character_voice(self, character_name):
    voice_config = CharacterVoice.get_character_voice(character_name)
    engine = voice_config.get('engine')
    
    if engine == 'edge-tts':
        voice = voice_config.get('voice')
        self.tts = TTS.EdgeTTS(voice=voice)  # 创建新TTS实例
```

## 🎓 学习资源

- **GPT-SoVITS 官方**: https://github.com/RVC-Boss/GPT-SoVITS
- **Edge-TTS 官方**: https://github.com/rany2/edge-tts
- **VITS 项目**: https://github.com/jaywalnut310/vits
- **Bert-VITS2**: https://github.com/fishaudio/Bert-VITS2
- **UVR 人声分离**: https://github.com/Anjok07/ultimatevocalremovergui
- **配置指南**: [docs/CHARACTER_VOICE_GUIDE.md](docs/CHARACTER_VOICE_GUIDE.md)

## 📝 更新日志

### v1.1 (2026-01-07)
- ✨ 新增 GPT-SoVITS 语音合成支持，支持 5-10 秒少样本克隆真实角色语音
- 📝 完善 GPT-SoVITS 部署与配置说明文档
- 📊 添加各 TTS 引擎（Edge-TTS, VITS, GPT-SoVITS）的技术对比与选型建议
- 🔧 优化角色语音映射配置建议

### v1.0 (2026-01-01)
- ✨ 实现基于声纹的角色语音切换
- ✨ 支持 Edge-TTS 多音色
- ✨ 添加角色配置管理工具
- ✨ 添加测试和验证插件
- 📝 完善文档和使用指南

## 🔮 未来计划

- [ ] 支持情感标签（开心、难过、生气）
- [ ] 实时语音克隆
- [ ] Web界面配置
- [ ] 更多TTS引擎适配
- [ ] 角色音色市场

## 💡 贡献

欢迎提交 Issue 和 Pull Request！

## ⚖️ 注意事项

1. **版权**: 角色语音涉及版权，仅供个人学习使用
2. **隐私**: 声纹数据仅本地存储，注意保护隐私
3. **资源**: VITS 等模型需要较多计算资源
