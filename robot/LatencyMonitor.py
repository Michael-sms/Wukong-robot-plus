# -*- coding: utf-8 -*-
"""
全链路延迟监控模块
负责监控语音机器人的完整交互链路延迟，包括：
- 唤醒检测延迟
- ASR识别延迟
- NLU理解延迟
- 技能处理延迟
- TTS合成延迟
- 音频播放延迟
- WebSocket通信抖动

生成量化的延迟分析报告，保证局域网环境下不出现断音
"""

import time
import json
import os
import threading
from collections import deque
from datetime import datetime
from robot import logging, constants

logger = logging.getLogger(__name__)


class LatencyTracker:
    """单次对话的延迟追踪器"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.timestamps = {}
        self.durations = {}
        self.start_time = time.time()
        
    def mark(self, stage_name):
        """标记时间点"""
        self.timestamps[stage_name] = time.time()
        
    def calculate_duration(self, stage_name, start_stage, end_stage):
        """计算两个阶段之间的延迟"""
        if start_stage in self.timestamps and end_stage in self.timestamps:
            duration = (self.timestamps[end_stage] - self.timestamps[start_stage]) * 1000
            self.durations[stage_name] = duration
            return duration
        return None
    
    def get_total_latency(self):
        """获取总延迟"""
        if 'session_start' in self.timestamps and 'response_end' in self.timestamps:
            return (self.timestamps['response_end'] - self.timestamps['session_start']) * 1000
        return None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'timestamps': self.timestamps,
            'durations': self.durations,
            'total_latency': self.get_total_latency()
        }


class WebSocketJitterMonitor:
    """WebSocket通信抖动监控"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.latencies = deque(maxlen=window_size)
        self.packet_loss_count = 0
        self.total_packets = 0
        self.lock = threading.Lock()
        
    def record_latency(self, latency_ms):
        """记录单次延迟"""
        with self.lock:
            self.latencies.append(latency_ms)
            self.total_packets += 1
            
    def record_packet_loss(self):
        """记录丢包"""
        with self.lock:
            self.packet_loss_count += 1
            self.total_packets += 1
            
    def get_stats(self):
        """获取统计信息"""
        with self.lock:
            if not self.latencies:
                return None
                
            latency_list = list(self.latencies)
            avg_latency = sum(latency_list) / len(latency_list)
            max_latency = max(latency_list)
            min_latency = min(latency_list)
            
            # 计算抖动（连续延迟的差值）
            jitter_values = [abs(latency_list[i] - latency_list[i-1]) 
                           for i in range(1, len(latency_list))]
            avg_jitter = sum(jitter_values) / len(jitter_values) if jitter_values else 0
            max_jitter = max(jitter_values) if jitter_values else 0
            
            # 丢包率
            packet_loss_rate = (self.packet_loss_count / self.total_packets * 100) if self.total_packets > 0 else 0
            
            return {
                'avg_latency': round(avg_latency, 2),
                'max_latency': round(max_latency, 2),
                'min_latency': round(min_latency, 2),
                'avg_jitter': round(avg_jitter, 2),
                'max_jitter': round(max_jitter, 2),
                'packet_loss_rate': round(packet_loss_rate, 2),
                'sample_count': len(latency_list)
            }


class LatencyMonitor:
    """全链路延迟监控器"""
    
    def __init__(self):
        self.sessions = {}  # 存储所有会话的延迟数据
        self.ws_monitor = WebSocketJitterMonitor()
        self.report_dir = os.path.join(constants.TEMP_PATH, 'latency_reports')
        self.lock = threading.Lock()
        
        # 创建报告目录
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
            
        # 延迟阈值（毫秒）- 根据实际网络服务延迟调整
        self.thresholds = {
            'wakeup': 500,      # 唤醒延迟阈值（放宽到500ms）
            'asr': 1500,        # ASR延迟阈值（网络语音识别服务，1.5秒合理）
            'nlu': 800,         # NLU延迟阈值（网络NLU服务，800ms合理）
            'skill': 3000,      # 技能处理延迟阈值（包含复杂逻辑+多次TTS，3秒合理）
            'tts': 5000,        # TTS合成延迟阈值（Edge-TTS网络服务，长文本5秒内）
            'play': 500,        # 播放延迟阈值（本地播放，放宽到500ms）
            'total': 15000,     # 总延迟阈值（15秒内完成一次完整交互）
            'ws_latency': 100,  # WebSocket延迟阈值（放宽到100ms）
            'ws_jitter': 50     # WebSocket抖动阈值（放宽到50ms）
        }
        
        logger.info("全链路延迟监控器已初始化")
        
    def start_session(self, session_id):
        """开始新的会话追踪"""
        with self.lock:
            tracker = LatencyTracker(session_id)
            tracker.mark('session_start')
            self.sessions[session_id] = tracker
            logger.debug(f"开始延迟追踪: {session_id}")
            return tracker
    
    def mark_stage(self, session_id, stage_name):
        """标记某个阶段的时间点"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].mark(stage_name)
                logger.debug(f"[{session_id}] 标记阶段: {stage_name}")
            else:
                logger.warning(f"会话 {session_id} 不存在")
    
    def end_session(self, session_id):
        """结束会话并计算各阶段延迟"""
        with self.lock:
            if session_id not in self.sessions:
                logger.warning(f"会话 {session_id} 不存在")
                return None
                
            tracker = self.sessions[session_id]
            tracker.mark('session_end')
            
            # 计算各阶段延迟
            stages = [
                ('wakeup_latency', 'session_start', 'wakeup_detected'),
                ('asr_latency', 'asr_start', 'asr_end'),
                ('nlu_latency', 'nlu_start', 'nlu_end'),
                ('skill_latency', 'skill_start', 'skill_end'),
                ('tts_latency', 'tts_start', 'tts_end'),
                ('play_latency', 'play_start', 'play_end'),
                ('response_latency', 'session_start', 'response_end')
            ]
            
            for stage_name, start, end in stages:
                tracker.calculate_duration(stage_name, start, end)
            
            # 分析并记录
            self._analyze_and_log(tracker)
            
            return tracker
    
    def _analyze_and_log(self, tracker):
        """分析延迟并记录警告"""
        logger.info(f"\n{'='*60}")
        logger.info(f"会话 {tracker.session_id} 延迟分析")
        logger.info(f"{'='*60}")
        
        for stage_name, latency in tracker.durations.items():
            if latency is None:
                continue
                
            # 获取阈值
            threshold_key = stage_name.replace('_latency', '')
            threshold = self.thresholds.get(threshold_key, float('inf'))
            
            # 判断是否达标
            status = "✅ 达标" if latency <= threshold else "⚠️ 超标"
            logger.info(f"{stage_name}: {latency:.2f}ms (阈值: {threshold}ms) {status}")
        
        total = tracker.get_total_latency()
        if total:
            status = "✅ 达标" if total <= self.thresholds['total'] else "⚠️ 超标"
            logger.info(f"总延迟: {total:.2f}ms (阈值: {self.thresholds['total']}ms) {status}")
        
        logger.info(f"{'='*60}\n")
    
    def record_ws_latency(self, latency_ms):
        """记录WebSocket延迟"""
        self.ws_monitor.record_latency(latency_ms)
        
        # 检查是否超过阈值
        if latency_ms > self.thresholds['ws_latency']:
            logger.warning(f"⚠️ WebSocket延迟过高: {latency_ms:.2f}ms (阈值: {self.thresholds['ws_latency']}ms)")
    
    def record_ws_packet_loss(self):
        """记录WebSocket丢包"""
        self.ws_monitor.record_packet_loss()
        logger.warning("⚠️ WebSocket丢包")
    
    def get_ws_stats(self):
        """获取WebSocket统计信息"""
        stats = self.ws_monitor.get_stats()
        if stats:
            logger.info(f"\n{'='*60}")
            logger.info(f"WebSocket通信统计")
            logger.info(f"{'='*60}")
            logger.info(f"平均延迟: {stats['avg_latency']}ms")
            logger.info(f"最大延迟: {stats['max_latency']}ms")
            logger.info(f"最小延迟: {stats['min_latency']}ms")
            logger.info(f"平均抖动: {stats['avg_jitter']}ms")
            logger.info(f"最大抖动: {stats['max_jitter']}ms")
            logger.info(f"丢包率: {stats['packet_loss_rate']}%")
            logger.info(f"样本数: {stats['sample_count']}")
            logger.info(f"{'='*60}\n")
            
            # 检查抖动
            if stats['avg_jitter'] > self.thresholds['ws_jitter']:
                logger.warning(f"⚠️ WebSocket抖动过高，可能导致断音！")
        
        return stats
    
    def generate_report(self, output_file=None):
        """生成延迟分析报告"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.report_dir, f'latency_report_{timestamp}.json')
        
        with self.lock:
            report = {
                'generated_at': datetime.now().isoformat(),
                'sessions': [tracker.to_dict() for tracker in self.sessions.values()],
                'websocket_stats': self.ws_monitor.get_stats(),
                'thresholds': self.thresholds,
                'summary': self._generate_summary()
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"延迟分析报告已生成: {output_file}")
        return output_file
    
    def _generate_summary(self):
        """生成摘要统计"""
        if not self.sessions:
            return None
        
        all_totals = [t.get_total_latency() for t in self.sessions.values() 
                     if t.get_total_latency() is not None]
        
        if not all_totals:
            return None
        
        return {
            'total_sessions': len(self.sessions),
            'avg_total_latency': round(sum(all_totals) / len(all_totals), 2),
            'max_total_latency': round(max(all_totals), 2),
            'min_total_latency': round(min(all_totals), 2),
            'sessions_over_threshold': sum(1 for t in all_totals if t > self.thresholds['total'])
        }
    
    def clear_old_sessions(self, keep_last=100):
        """清理旧会话数据，保留最近的N个"""
        with self.lock:
            if len(self.sessions) > keep_last:
                sorted_sessions = sorted(self.sessions.items(), 
                                       key=lambda x: x[1].start_time)
                to_remove = sorted_sessions[:-keep_last]
                for session_id, _ in to_remove:
                    del self.sessions[session_id]
                logger.info(f"清理了 {len(to_remove)} 个旧会话数据")


# 全局单例
_latency_monitor = None

def get_monitor():
    """获取全局延迟监控器实例"""
    global _latency_monitor
    if _latency_monitor is None:
        _latency_monitor = LatencyMonitor()
    return _latency_monitor
