# -*- coding: utf-8 -*-
from robot import config, logging, CharacterVoice
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):
    SLUG = "test_character_voice"

    def handle(self, text, parsed):
        """测试角色语音功能"""
        
        # 获取当前用户的角色偏好
        if self.con.current_user_context:
            fav_char = self.con.current_user_context.get('fav_char')
            if fav_char:
                self.say(f"你好！我现在使用的是{fav_char}的语音。", wait=True)
                self.say("这是一段测试语音，听听看效果如何。", wait=True)
                
                # 显示当前TTS配置
                if hasattr(self.con.tts, 'voice'):
                    voice = self.con.tts.voice
                    logger.info(f"当前TTS音色: {voice}")
                    self.say(f"当前使用的音色代码是 {voice}。")
                else:
                    logger.info(f"当前TTS引擎: {self.con.tts.SLUG}")
                    self.say(f"当前使用的TTS引擎是 {self.con.tts.SLUG}。")
            else:
                self.say("你还没有设置喜欢的角色，我使用默认语音。")
        else:
            self.say("我还没有识别到你的身份，使用的是默认语音。")
            self.say("你可以先注册声纹并选择喜欢的角色。")
        
        # 列出所有可用的角色配置
        available_chars = CharacterVoice.list_available_characters()
        if available_chars:
            char_list = "、".join(available_chars)
            self.say(f"目前系统已配置的角色有：{char_list}。", wait=True)
            logger.info(f"已配置角色: {available_chars}")

    def isValid(self, text, parsed):
        return any(word in text for word in ["测试语音", "测试角色", "角色语音测试", "当前语音"])
