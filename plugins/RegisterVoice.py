# -*- coding: utf-8 -*-
import time
import os
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):
    SLUG = "register_voice"

    def handle(self, text, parsed):
        # 录音参数配置
        # silent_threshold: 静音检测阈值，值越大等待用户说完的时间越长（默认150，这里用200给用户更多思考时间）
        # recording_timeout: 最大录音时长（秒）
        normal_silent_threshold = 200  # 普通对话的静音阈值
        voice_sample_silent_threshold = 300  # 声纹采集的静音阈值（更长，等用户说完）
        voice_sample_timeout = 15  # 声纹采集最大录音时长（秒）
        
        # 步骤1: 询问用户名字
        self.say("好的，我要开始记录你的声纹了。请在滴声后告诉我你的名字。", wait=True)
        
        name_response = self.con.activeListen(silent_threshold=normal_silent_threshold)
        if not name_response:
            self.say("抱歉，我没有听清你的名字，请重新开始注册。")
            return
        
        # 从回复中提取名字（简单处理：去除常见前缀）
        name = self._extract_name(name_response)
        if not name:
            name = name_response.strip()
        
        logger.info(f"获取到用户名字: {name}")
        
        # 步骤2: 询问喜欢的角色（可选）
        self.say(f"好的，{name}。请在滴声后告诉我你喜欢的角色名字，或者说\"跳过\"。", wait=True)
        
        fav_char_response = self.con.activeListen(silent_threshold=normal_silent_threshold)
        fav_char = None
        if fav_char_response and "跳过" not in fav_char_response:
            fav_char = fav_char_response.strip()
            logger.info(f"获取到喜欢的角色: {fav_char}")
        
        # 步骤3: 询问角色定位（可选）
        self.say('请在滴声后告诉我你希望我怎么称呼你，比如"主人"、"朋友"，或者说"跳过"。', wait=True)
        
        role_response = self.con.activeListen(silent_threshold=normal_silent_threshold)
        role = "user"  # 默认角色
        if role_response and "跳过" not in role_response:
            role = role_response.strip()
            logger.info(f"获取到角色定位: {role}")
        
        # 步骤4: 录制声纹样本
        self.say("很好！现在请在滴声后随便说一段话，我会记录你的声纹特征。说得越长越准确哦。", wait=True)
        
        # 主动开启一次录音，获取文件路径
        # 使用更长的静音阈值和录音超时，确保用户有足够时间说话
        fp = self.con.activeListen(return_fp=True, silent_threshold=voice_sample_silent_threshold, recording_timeout=voice_sample_timeout)

        if not fp:
            self.say("抱歉，我没有获取到刚才的录音，请重试。")
            return

        try:
            with open(fp, 'rb') as f:
                audio_data = f.read()
            # 手动删除临时文件
            os.remove(fp)
        except Exception as e:
            logger.error(f"读取录音文件失败: {e}")
            self.say("抱歉，读取录音文件时出错，请重试。")
            return

        # 步骤5: 调用声纹模块注册
        user_id = f"user_{int(time.time())}"
        anime_context = {
            "fav_char": fav_char,
            "role": role
        }

        success = self.con.speaker_id.register_user(audio_data, user_id, name, anime_context)

        if success:
            if fav_char:
                self.say(f"注册成功！已记住你的声音，{name}。以后我会用{fav_char}的语气和你对话。")
            else:
                self.say(f"注册成功！已记住你的声音，{name}。")
        else:
            self.say("声纹提取失败，请在安静环境下重试。")

    def _extract_name(self, text):
        """
        从用户回复中提取名字
        处理类似 "我叫小明"、"我是小红"、"叫我阿强" 等格式
        """
        prefixes = ["我叫", "我是", "叫我", "我的名字是", "名字是", "我名字叫"]
        text = text.strip()
        
        for prefix in prefixes:
            if prefix in text:
                # 提取前缀后面的内容
                name = text.split(prefix)[-1].strip()
                # 去除可能的后缀
                suffixes = ["。", "，", "啊", "呀", "吧", "呢"]
                for suffix in suffixes:
                    if name.endswith(suffix):
                        name = name[:-1]
                return name if name else None
        
        return None

    def isValid(self, text, parsed):
        return any(word in text for word in ["注册声纹", "记住我的声音"])