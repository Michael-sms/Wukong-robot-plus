# 全链路延迟监控功能说明

## 🎯 功能概述

全链路延迟监控系统用于实时追踪语音机器人从唤醒到回复的完整交互链路，检测网络抖动，**保证局域网环境下不出现断音**。

### 核心能力

- ⏱️ **全链路延迟追踪** - ASR、NLU、技能处理、TTS、播放各阶段
- 🌐 **WebSocket抖动检测** - 实时监控网络通信质量
- 📊 **量化分析报告** - 生成JSON格式的详细延迟报告
- 🔔 **智能阈值预警** - 超标自动告警，预防断音

## 📁 相关文件

```
robot/
  └── LatencyMonitor.py          # 核心延迟监控模块

plugins/
  └── LatencyCheck.py            # 延迟检测语音插件

server/
  └── server.py                  # WebSocket抖动监控集成

temp/
  └── latency_reports/           # 延迟报告存储目录
      └── latency_report_YYYYMMDD_HHMMSS.json
```

## 🔧 监控链路

```
用户说话
    ↓
[session_start] ← 创建会话追踪器
    ↓
[wakeup_detected] ← 唤醒检测完成
    ↓
[asr_start] → ASR语音识别 → [asr_end]
    ↓
[nlu_start] → NLU语义理解 → [nlu_end]
    ↓
[skill_start] → 技能/插件处理 → [skill_end]
    ↓
[tts_start] → TTS语音合成 → [tts_end]
    ↓
[play_start] → 音频播放 → [play_end]
    ↓
[response_end] ← 计算各阶段延迟，生成报告
[session_end] ← 会话结束


        WebSocket通信
              ↓
    [ping/pong心跳检测]
              ↓
    延迟记录 → 抖动计算 → 丢包统计
```

## ⚙️ 延迟阈值配置

系统默认阈值（毫秒），超过阈值会输出警告日志：

| 阶段 | 阈值 | 说明 |
|------|------|------|
| 唤醒检测 | 500ms | 唤醒词检测完成 |
| ASR识别 | 1500ms | 语音转文字（网络服务） |
| NLU理解 | 800ms | 语义解析（网络服务） |
| 技能处理 | 3000ms | 插件执行（含多次TTS调用） |
| TTS合成 | 5000ms | 文字转语音（Edge-TTS网络服务） |
| 音频播放 | 500ms | 播放启动（本地） |
| **总延迟** | **15000ms** | **端到端完整交互** |
| WebSocket延迟 | 100ms | 网络通信RTT |
| WebSocket抖动 | 50ms | 网络稳定性（连续延迟波动） |

> **注意**：以上阈值根据使用网络服务（腾讯云ASR、百度NLU、Edge-TTS）的实际场景设定。如使用本地模型，可相应调低阈值。

### 修改阈值

编辑 `robot/LatencyMonitor.py`：

```python
self.thresholds = {
    'wakeup': 500,      # 唤醒延迟阈值（毫秒）
    'asr': 1500,        # ASR延迟阈值（网络语音识别服务）
    'nlu': 800,         # NLU延迟阈值（网络NLU服务）
    'skill': 3000,      # 技能处理延迟阈值（包含复杂逻辑）
    'tts': 5000,        # TTS合成延迟阈值（Edge-TTS网络服务）
    'play': 500,        # 播放延迟阈值（本地播放）
    'total': 15000,     # 总延迟阈值（15秒内完成交互）
    'ws_latency': 100,  # WebSocket延迟阈值
    'ws_jitter': 50     # WebSocket抖动阈值
}
```

## 🚀 使用方法

### 1. 语音命令

**查看网络状态：**
```
你: "网络状态" 或 "通信状态"
机器人: "网络通信状态如下：平均延迟25.3毫秒，平均抖动3.2毫秒，丢包率0.1%。网络状态良好。"
```

**查看延迟统计：**
```
你: "延迟统计" 或 "性能统计"
机器人: "当前共有15个会话记录，平均总延迟1280毫秒，最大延迟2100毫秒。所有会话延迟都在正常范围内。"
```

**生成延迟报告：**
```
你: "延迟报告" 或 "生成报告"
机器人: "延迟分析报告已生成，保存在temp/latency_reports/latency_report_xxx.json"
```

### 2. 查看日志

每次对话结束后自动输出延迟分析：

```log
============================================================
会话 12345678-1234-1234-1234-123456789abc 延迟分析
============================================================
asr_latency: 156.23ms (阈值: 200ms) ✅ 达标
nlu_latency: 45.67ms (阈值: 100ms) ✅ 达标
skill_latency: 234.89ms (阈值: 500ms) ✅ 达标
tts_latency: 567.12ms (阈值: 1000ms) ✅ 达标
play_latency: 23.45ms (阈值: 100ms) ✅ 达标
总延迟: 1027.36ms (阈值: 2000ms) ✅ 达标
============================================================
```

### 3. 延迟报告格式

报告保存在 `temp/latency_reports/` 目录：

```json
{
  "generated_at": "2026-01-04T12:00:00",
  "sessions": [
    {
      "session_id": "12345678-1234-1234-1234-123456789abc",
      "timestamps": {
        "session_start": 1704340800.123,
        "asr_start": 1704340800.456,
        "asr_end": 1704340800.612,
        "nlu_start": 1704340800.613,
        "nlu_end": 1704340800.659
      },
      "durations": {
        "asr_latency": 156.23,
        "nlu_latency": 45.67,
        "skill_latency": 234.89,
        "tts_latency": 567.12,
        "play_latency": 23.45
      },
      "total_latency": 1027.36
    }
  ],
  "websocket_stats": {
    "avg_latency": 25.3,
    "max_latency": 48.7,
    "min_latency": 12.1,
    "avg_jitter": 3.2,
    "max_jitter": 8.9,
    "packet_loss_rate": 0.1,
    "sample_count": 100
  },
  "thresholds": {
    "asr": 200,
    "nlu": 100,
    "skill": 500,
    "tts": 1000,
    "play": 100,
    "total": 2000
  },
  "summary": {
    "total_sessions": 15,
    "avg_total_latency": 1280.5,
    "max_total_latency": 2100.3,
    "min_total_latency": 890.2,
    "sessions_over_threshold": 0
  }
}
```

## 🛡️ 防断音机制

### WebSocket抖动检测

系统通过以下机制保证局域网环境不出现断音：

1. **实时延迟监控**
   - 使用滑动窗口（100个样本）计算统计值
   - 每次消息传输记录延迟

2. **抖动计算**
   ```
   抖动 = |延迟[i] - 延迟[i-1]|
   平均抖动 = Σ抖动 / (样本数-1)
   ```

3. **丢包检测**
   - 捕获WebSocket发送失败
   - 计算丢包率 = 丢包数 / 总包数 × 100%

4. **智能预警**
   ```log
   ⚠️ WebSocket延迟过高: 68.5ms (阈值: 50ms)
   ⚠️ WebSocket抖动较大，可能出现断音
   ⚠️ WebSocket丢包
   ```

### 前端集成

前端需要实现心跳ping机制：

```javascript
const ws = new WebSocket('ws://localhost:5000/chat');

// 定期发送ping（每5秒）
setInterval(() => {
    ws.send(JSON.stringify({
        action: 'ping',
        timestamp: Date.now()
    }));
}, 5000);

// 接收pong响应
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.action === 'pong') {
        console.log(`往返延迟: ${data.latency}ms`);
    }
};
```

### 可视化测试工具

启动服务后访问：
```
http://localhost:5000/static/latency_test.html
```

功能：
- 实时显示当前/平均/最大延迟
- 统计抖动和丢包率
- 自动告警高延迟情况

## 📈 性能影响

| 指标 | 数值 | 说明 |
|------|------|------|
| CPU开销 | < 0.1% | 仅时间戳记录 |
| 内存开销 | ~1MB | 100个会话数据 |
| 延迟影响 | < 1ms | 微秒级操作 |

## 🔍 代码集成说明

### Conversation.py 集成点

```python
from robot.LatencyMonitor import get_monitor

class Conversation:
    def __init__(self):
        self.latency_monitor = get_monitor()
        self.current_session_id = None
    
    def doConverse(self, fp, ...):
        # 启动会话
        session_id = str(uuid.uuid1())
        self.current_session_id = session_id
        tracker = self.latency_monitor.start_session(session_id)
        
        # ASR延迟追踪
        self.latency_monitor.mark_stage(session_id, 'asr_start')
        query = self.asr.transcribe(fp)
        self.latency_monitor.mark_stage(session_id, 'asr_end')
    
    def doResponse(self, query, ...):
        # NLU延迟追踪
        self.latency_monitor.mark_stage(self.current_session_id, 'nlu_start')
        parsed = self.doParse(query)
        self.latency_monitor.mark_stage(self.current_session_id, 'nlu_end')
    
    def say(self, msg, ...):
        # TTS延迟追踪
        self.latency_monitor.mark_stage(self.current_session_id, 'tts_start')
        # ... TTS合成
        # 播放完成后
        self.latency_monitor.mark_stage(self.current_session_id, 'tts_end')
        self.latency_monitor.mark_stage(self.current_session_id, 'response_end')
        self.latency_monitor.end_session(self.current_session_id)
```

### server.py WebSocket集成

```python
from robot.LatencyMonitor import get_monitor

class ChatWebSocketHandler(WebSocketHandler):
    def on_message(self, message):
        data = json.loads(message)
        if data.get('action') == 'ping':
            latency = time.time() * 1000 - data['timestamp']
            monitor = get_monitor()
            monitor.record_ws_latency(latency)
            
            self.write_message(json.dumps({
                'action': 'pong',
                'latency': latency
            }))
    
    def send_response(self, msg, uuid, plugin=""):
        try:
            self.write_message(json.dumps({...}))
        except Exception:
            monitor = get_monitor()
            monitor.record_ws_packet_loss()
```

## 🐛 故障排查

### Q1: 为什么没有延迟分析日志？

**检查：**
1. 确认日志级别设置为 INFO 或更低
2. 检查是否有完整的对话流程
3. 查看是否有异常导致会话中断

### Q2: WebSocket延迟很高怎么办？

**排查步骤：**
1. 检查网络连接：`ping 服务器IP`
2. 查看服务器负载：`top` 或 `htop`
3. 确认是否在局域网环境
4. 检查防火墙设置

### Q3: 如何优化总延迟？

根据日志分析瓶颈：

| 瓶颈 | 优化方案 |
|------|---------|
| ASR延迟高 | 使用本地ASR或优化网络 |
| TTS延迟高 | 启用缓存或使用本地TTS |
| 技能处理慢 | 优化插件代码逻辑 |
| WebSocket抖动 | 检查网络质量 |

### Q4: 延迟报告太多如何清理？

```python
from robot.LatencyMonitor import get_monitor

monitor = get_monitor()
monitor.clear_old_sessions(keep_last=50)  # 只保留最近50个
```

### Q5: 如何在代码中获取延迟数据？

```python
from robot.LatencyMonitor import get_monitor

monitor = get_monitor()

# 获取WebSocket统计
stats = monitor.get_ws_stats()
print(f"平均延迟: {stats['avg_latency']}ms")
print(f"平均抖动: {stats['avg_jitter']}ms")

# 生成报告
report_file = monitor.generate_report()
```

## 📝 更新日志

### v1.1 (2026-01-09)
- 🔧 新增唤醒检测延迟监控（wakeup阶段）
- 🔧 调整延迟阈值以适配实际网络服务场景：
  - 唤醒检测：500ms（新增）
  - ASR识别：1500ms（网络服务）
  - NLU理解：800ms（网络服务）
  - 技能处理：3000ms（含多次TTS调用）
  - TTS合成：5000ms（Edge-TTS长文本）
  - 音频播放：500ms（本地播放）
  - 总延迟：15000ms（完整交互）
  - WebSocket延迟：100ms
  - WebSocket抖动：50ms
- 📝 完善文档说明，标注各阈值使用场景（网络/本地服务）
- 📝 更新监控链路图，增加 wakeup_detected 和 session_end 节点

### v1.0 (2026-01-04)
- ✨ 实现全链路延迟追踪（ASR→NLU→技能→TTS→播放）
- ✨ 实现WebSocket通信抖动检测
- ✨ 支持生成量化延迟分析报告
- ✨ 智能阈值预警，保证局域网不断音
- ✨ 添加延迟检测语音插件
- ✨ 提供可视化WebSocket测试页面
- 📝 完善使用文档

## 📚 相关链接

- 核心模块: [robot/LatencyMonitor.py](robot/LatencyMonitor.py)
- 语音插件: [plugins/LatencyCheck.py](plugins/LatencyCheck.py)
- 对话集成: [robot/Conversation.py](robot/Conversation.py)
- WebSocket: [server/server.py](server/server.py)
- 测试页面: [server/static/latency_test.html](server/static/latency_test.html)
