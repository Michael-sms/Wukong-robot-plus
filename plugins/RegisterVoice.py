# -*- coding: utf-8 -*-
import time
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):
    SLUG = "register_voice"

    def handle(self, text, parsed):
        '''
        # 1. 确认意图
        self.say("好的，我要开始记录你的声纹了。请在听到滴声后，清晰地说出：我是老三，我喜欢千早爱音。", wait=True)
        
        # 2. 录制音频 (复用 Conversation 的录音逻辑，或者这里简单等待用户说话)
        # 注意：这里需要获取 Conversation 实例来拿到最近一次的录音文件
        # 由于插件机制限制，通常我们取最近一次对话的音频，或者发起一次新的主动聆听
        
        # 这里的 activeListen 是 Conversation 的方法，插件里通常拿不到
        # 变通方法：让用户再说一句话，作为注册样本
        
        self.con.doConverse(None, onSay=None) # 触发一次主动交互流程不太合适
        
        # 更简单的方案：直接使用触发这句话的那段录音 (如果 Conversation 保存了的话)
        # 假设 Conversation.py 中把最近一次录音路径存在了 self.con.last_audio_fp
        
        audio_fp = getattr(self.con, 'last_audio_fp', None)
        
        if not audio_fp:
            self.say("抱歉，我没有获取到刚才的录音，请重试。")
            return

        # 3. 读取音频文件
        with open(audio_fp, 'rb') as f:
            audio_data = f.read()
        '''
        self.say("好的，请在滴声后随便说一句话。", wait=True)
        
        # 主动开启一次录音
        fp = self.con.activeListen(return_fp=True)

        if not fp:
            self.say("抱歉，我没有获取到刚才的录音，请重试。")
            return

        
        try:
            with open(fp, 'rb') as f:
                audio_data = f.read()
            # 手动删除临时文件
            import os
            os.remove(fp)
        except Exception as e:
            logger.error(f"读取录音文件失败: {e}")
            self.say("抱歉，读取录音文件时出错，请重试。")
            return

        # 4. 调用声纹模块注册
        # 假设 anime_context 是硬编码的，或者通过多轮对话获取
        # 这里为了演示，先写死
        user_id = f"user_{int(time.time())}"
        name = "老三" # 可以通过 NLU 提取名字
        anime_context = {
            "fav_char": "千早爱音",
            "role": "master"
        }

        success = self.con.speaker_id.register_user(audio_data, user_id, name, anime_context)

        if success:
            self.say(f"注册成功！已记住你的声音，{name}。以后我会用千早爱音的语气和你对话。")
        else:
            self.say("声纹提取失败，请在安静环境下重试。")

    def isValid(self, text, parsed):
        return any(word in text for word in ["注册声纹", "记住我的声音", "我是谁"])