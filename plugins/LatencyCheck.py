# -*- coding: utf-8 -*-
"""
延迟检测插件
用于测试和查看全链路延迟监控数据
"""

from robot.sdk.AbstractPlugin import AbstractPlugin
from robot.LatencyMonitor import get_monitor
import logging

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    
    SLUG = "latency_check"
    
    def __init__(self, con):
        super(Plugin, self).__init__(con)
    
    def handle(self, text, parsed):
        """处理指令"""
        monitor = get_monitor()
        
        if "延迟报告" in text or "生成报告" in text:
            # 生成延迟报告
            report_file = monitor.generate_report()
            self.say(f"延迟分析报告已生成，保存在{report_file}")
            
        elif "网络状态" in text or "通信状态" in text:
            # 查看WebSocket统计
            stats = monitor.get_ws_stats()
            if stats:
                msg = f"网络通信状态如下：平均延迟{stats['avg_latency']}毫秒，"
                msg += f"平均抖动{stats['avg_jitter']}毫秒，"
                msg += f"丢包率{stats['packet_loss_rate']}%。"
                
                if stats['avg_jitter'] > monitor.thresholds['ws_jitter']:
                    msg += "当前网络抖动较大，可能出现断音。"
                elif stats['packet_loss_rate'] > 1:
                    msg += "当前网络丢包较多，请检查网络连接。"
                else:
                    msg += "网络状态良好。"
                    
                self.say(msg)
            else:
                self.say("暂无网络统计数据")
                
        elif "延迟统计" in text or "性能统计" in text:
            # 查看延迟摘要
            summary = monitor._generate_summary()
            if summary:
                msg = f"当前共有{summary['total_sessions']}个会话记录，"
                msg += f"平均总延迟{summary['avg_total_latency']}毫秒，"
                msg += f"最大延迟{summary['max_total_latency']}毫秒。"
                
                if summary['sessions_over_threshold'] > 0:
                    msg += f"有{summary['sessions_over_threshold']}个会话超过阈值。"
                else:
                    msg += "所有会话延迟都在正常范围内。"
                    
                self.say(msg)
            else:
                self.say("暂无延迟统计数据")
        else:
            self.say("我可以帮你查看延迟报告、网络状态或延迟统计")
    
    def isValid(self, text, parsed):
        """判断是否匹配插件"""
        return any(word in text for word in [
            "延迟报告", "生成报告", 
            "网络状态", "通信状态",
            "延迟统计", "性能统计"
        ])
