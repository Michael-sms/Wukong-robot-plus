import webrtcvad
import numpy as np

class OptimizedVAD:
    def __init__(self, sample_rate=16000, frame_duration=30, level=3):
        self.vad = webrtcvad.Vad(level)
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.energy_threshold = 500 # 动态能量阈值基准

    def is_speech(self, frame, energy_boost=1.2):
        # 1. 能量阈值检测 (简单快速)
        audio_data = np.frombuffer(frame, dtype=np.int16)
        energy = np.sqrt(np.mean(audio_data**2))
        
        # 2. WebRTC VAD 检测 (语义/频率特征)
        is_speech_vad = self.vad.is_speech(frame, self.sample_rate)
        
        # 结合两者：能量需超过阈值且 VAD 判定为语音
        return is_speech_vad and energy > self.energy_threshold