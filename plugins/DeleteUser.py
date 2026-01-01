# -*- coding: utf-8 -*-
import json
import os
from robot import config, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):
    SLUG = "delete_user"

    def handle(self, text, parsed):
        """删除已注册的用户"""
        
        users = self.con.speaker_id.users
        
        if not users:
            self.say("目前没有已注册的用户。")
            return
        
        # 步骤1: 列出所有用户
        user_count = len(users)
        self.say(f"目前有{user_count}个已注册用户。我来为你列出来。", wait=True)
        
        # 构建用户列表，用编号标识
        user_list = []
        for idx, user in enumerate(users, 1):
            name = user.get('name', '未知')
            user_id = user.get('id', 'unknown')
            context = user.get('context', {})
            fav_char = context.get('fav_char', '未设置')
            role = context.get('role', '未设置')
            
            intro = f"编号{idx}，{name}"
            if fav_char and fav_char != '未设置':
                intro += f"，喜欢{fav_char}"
            
            self.say(intro, wait=True)
            user_list.append((idx, name, user_id))
            
            logger.info(f"用户 {idx}: {name} (ID: {user_id})")
        
        # 步骤2: 询问要删除的用户
        self.say("请在滴声后告诉我要删除的用户编号，比如说\"删除1号\"或\"删除编号2\"。如果不想删除，请说\"取消\"。", wait=True)
        
        response = self.con.activeListen(silent_threshold=200)
        
        if not response:
            self.say("没有听清，操作已取消。")
            return
        
        # 检查是否取消
        if "取消" in response or "不删" in response:
            self.say("好的，已取消删除操作。")
            return
        
        # 提取编号
        delete_idx = self._extract_number(response)
        
        if delete_idx is None or delete_idx < 1 or delete_idx > user_count:
            self.say(f"编号无效，请说1到{user_count}之间的数字。操作已取消。")
            return
        
        # 步骤3: 确认删除
        target_user = users[delete_idx - 1]
        target_name = target_user.get('name', '未知')
        
        self.say(f"确认要删除用户{target_name}吗？请说\"确认\"或\"取消\"。", wait=True)
        
        confirm = self.con.activeListen(silent_threshold=200)
        
        if not confirm or "确认" not in confirm:
            self.say("已取消删除操作。")
            return
        
        # 步骤4: 执行删除
        try:
            # 从列表中移除用户
            deleted_user = users.pop(delete_idx - 1)
            
            # 重建Faiss索引
            self._rebuild_index()
            
            # 保存到数据库文件
            db_path = self.con.speaker_id.db_path
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            self.say(f"已成功删除用户{target_name}。")
            logger.info(f"删除用户成功: {target_name} (ID: {deleted_user.get('id')})")
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            self.say("删除过程中出现错误，请查看日志。")

    def _rebuild_index(self):
        """重建Faiss索引"""
        try:
            import numpy as np
            import faiss
            
            speaker_id = self.con.speaker_id
            users = speaker_id.users
            
            # 清空旧索引
            speaker_id.index.reset()
            
            # 重新添加所有用户的向量
            if users:
                vectors = []
                for user in users:
                    if 'embedding' in user:
                        vectors.append(np.array(user['embedding'], dtype='float32'))
                
                if vectors:
                    matrix = np.vstack(vectors)
                    faiss.normalize_L2(matrix)
                    speaker_id.index.add(matrix)
                    logger.info(f"Faiss索引重建完成，当前用户数: {speaker_id.index.ntotal}")
            
        except Exception as e:
            logger.error(f"重建Faiss索引失败: {e}")
            raise

    def _extract_number(self, text):
        """从文本中提取数字"""
        import re
        
        # 处理中文数字
        chinese_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
            '6': 6, '7': 7, '8': 8, '9': 9, '10': 10
        }
        
        # 尝试提取阿拉伯数字
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        # 尝试匹配中文数字
        for ch_num, value in chinese_nums.items():
            if ch_num in text:
                return value
        
        return None

    def isValid(self, text, parsed):
        return any(word in text for word in ["删除用户", "移除用户", "取消注册"])
