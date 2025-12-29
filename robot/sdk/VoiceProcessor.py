import asyncio
import numpy as np
import onnxruntime
import pyaudio
import time
from robot import logging

logger = logging.getLogger(__name__)

class SileroPerception:
    def __init__(self, model_path='static/silero_vad.onnx', threshold=0.5, sample_rate=16000):
        # 1. 初始化 Silero VAD (ONNX 引擎)
        self.session = onnxruntime.InferenceSession(model_path)
        logger.info("=== [成员1优化] VoiceProcessor (Silero-VAD) 初始化成功 ===")
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.frame_size = 512  # Silero 推荐帧长
        
        # 2. 状态管理
        self.is_speaking = False
        self.energy_threshold = 500  # 能量基准
        self.queue = asyncio.Queue()
        
        # 3. ReSpeaker 配置 (通常为多通道，需取其中之一)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1, # 假设已通过驱动混音为单声道，或指定 index
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.frame_size
        )

    def get_energy(self, audio_data):
        """快速能量检测"""
        return np.sqrt(np.mean(np.frombuffer(audio_data, dtype=np.int16)**2))

    async def validate_vad(self, audio_frame):
        """Silero VAD 深度检测"""
        # 归一化
        audio_int16 = np.frombuffer(audio_frame, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        
        # ONNX 推理
        ort_inputs = {
            'input': audio_float32.reshape(1, -1),
            'sr': np.array([self.sample_rate], dtype=np.int64)
        }
        out = self.session.run(None, ort_inputs)
        return out[0][0][0] > self.threshold

    async def record_and_stream(self, ws_handler):
        """
        核心逻辑：录音即传、停顿即截
        ws_handler: 外部传入的 WebSocket 发送函数
        """
        logger.info("动漫角色感知系统已启动...")
        silence_frames = 0
        max_silence = 15 # 约 480ms 静音即截断
        
        while True:
            # 非阻塞读取音频
            data = self.stream.read(self.frame_size, exception_on_overflow=False)
            energy = self.get_energy(data)
            
            # 1. 能量初筛 (减少冗余切片)
            if energy < self.energy_threshold:
                if self.is_speaking:
                    silence_frames += 1
                else:
                    continue
            else:
                # 2. VAD 深度校验
                if await self.validate_vad(data):
                    if not self.is_speaking:
                        logger.info("检测到语音开始 -> 开启流式上传")
                        self.is_speaking = True
                    silence_frames = 0
                    # 录音即传：立即放入队列
                    await ws_handler.send(data)
                else:
                    if self.is_speaking:
                        silence_frames += 1

            # 3. 停顿即截 (语义预测/静音截断)
            if self.is_speaking and silence_frames > max_silence:
                logger.info("检测到静音截断 -> 发送结束标识")
                await ws_handler.send(b"END_OF_SPEECH")
                self.is_speaking = False
                silence_frames = 0
                # 降低延迟：此处可立即触发下一阶段逻辑，无需等待系统轮询

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()