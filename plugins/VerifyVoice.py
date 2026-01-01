# -*- coding: utf-8 -*-
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):
    SLUG = "verify_voice"

    def handle(self, text, parsed):
        """验证声纹识别功能"""
        
        # 提示用户说话
        self.say("请在滴声后随便说一段话，我会识别你是谁。", wait=True)
        
        # 录制音频
        fp = self.con.activeListen(return_fp=True, silent_threshold=200, recording_timeout=10)
        
        if not fp:
            self.say("抱歉，没有接收到录音，请重试。")
            return
        
        try:
            # 读取音频数据
            with open(fp, 'rb') as f:
                audio_data = f.read()
            
            # 调用声纹识别
            user, score = self.con.speaker_id.identify(audio_data)
            
            if user:
                name = user.get('name', '未知用户')
                user_id = user.get('id', 'unknown')
                context = user.get('context', {})
                fav_char = context.get('fav_char')
                role = context.get('role')
                
                # 构建回复信息
                response = f"识别成功！你是{name}，相似度为{score:.2f}。"
                
                if fav_char:
                    response += f" 你喜欢的角色是{fav_char}。"
                
                if role:
                    response += f" 我会叫你{role}。"
                
                logger.info(f"声纹验证成功 - 用户ID: {user_id}, 姓名: {name}, 相似度: {score:.2f}")
                self.say(response)
                
                # 显示详细信息到日志
                logger.info(f"用户详细信息 - ID: {user_id}")
                logger.info(f"  姓名: {name}")
                logger.info(f"  喜欢角色: {fav_char if fav_char else '未设置'}")
                logger.info(f"  角色定位: {role if role else '未设置'}")
                logger.info(f"  匹配相似度: {score:.2f}")
            else:
                self.say(f"未能识别出你的身份。最高相似度为{score:.2f}，低于识别阈值0.25。")
                logger.info(f"声纹验证失败 - 最高相似度: {score:.2f}")
                
        except Exception as e:
            logger.error(f"声纹验证出错: {e}")
            self.say("声纹验证过程中出现错误，请查看日志。")
        
        finally:
            # 清理临时文件
            import os
            if fp and os.path.exists(fp):
                os.remove(fp)

    def isValid(self, text, parsed):
        return any(word in text for word in ["验证声纹", "识别我", "我是谁", "测试声纹"])
