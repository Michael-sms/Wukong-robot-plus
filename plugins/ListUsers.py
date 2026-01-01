# -*- coding: utf-8 -*-
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):
    SLUG = "list_users"

    def handle(self, text, parsed):
        """列出所有已注册的用户"""
        
        users = self.con.speaker_id.users
        
        if not users:
            self.say("目前还没有注册任何用户。")
            logger.info("用户数据库为空")
            return
        
        # 统计信息
        user_count = len(users)
        self.say(f"目前共有{user_count}个已注册用户。我来为你介绍一下。", wait=True)
        
        # 逐个介绍用户
        for idx, user in enumerate(users, 1):
            name = user.get('name', '未知')
            user_id = user.get('id', 'unknown')
            context = user.get('context', {})
            fav_char = context.get('fav_char')
            role = context.get('role')
            
            # 构建介绍语
            intro = f"第{idx}位，{name}。"
            
            if fav_char:
                intro += f"喜欢的角色是{fav_char}。"
            
            if role:
                intro += f"希望被称呼为{role}。"
            
            self.say(intro, wait=True)
            
            # 记录到日志
            logger.info(f"用户 {idx}: {name}")
            logger.info(f"  ID: {user_id}")
            logger.info(f"  喜欢角色: {fav_char if fav_char else '未设置'}")
            logger.info(f"  角色定位: {role if role else '未设置'}")
        
        self.say("以上就是所有已注册的用户信息。")

    def isValid(self, text, parsed):
        return any(word in text for word in ["查看用户", "用户列表", "已注册用户", "有哪些用户"])
