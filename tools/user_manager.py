# -*- coding: utf-8 -*-
"""
用户管理工具 - 提供命令行方式直接管理已注册用户
可以通过修改此文件或运行脚本来管理用户数据库
"""
import json
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_path='static/user_db.json'):
        self.db_path = db_path
        self.users = []
        self.load_users()
    
    def load_users(self):
        """加载用户数据"""
        if not os.path.exists(self.db_path):
            print(f"数据库文件不存在: {self.db_path}")
            return
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.users = json.load(f)
        
        print(f"已加载 {len(self.users)} 个用户")
    
    def list_users(self):
        """列出所有用户"""
        if not self.users:
            print("没有已注册的用户")
            return
        
        print("\n" + "="*60)
        print("已注册用户列表")
        print("="*60)
        
        for idx, user in enumerate(self.users, 1):
            name = user.get('name', '未知')
            user_id = user.get('id', 'unknown')
            context = user.get('context', {})
            fav_char = context.get('fav_char', '未设置')
            role = context.get('role', '未设置')
            
            print(f"\n编号: {idx}")
            print(f"  姓名: {name}")
            print(f"  用户ID: {user_id}")
            print(f"  喜欢角色: {fav_char}")
            print(f"  角色定位: {role}")
        
        print("\n" + "="*60)
    
    def delete_user(self, index):
        """删除指定编号的用户"""
        if index < 1 or index > len(self.users):
            print(f"编号无效，请输入1到{len(self.users)}之间的数字")
            return False
        
        deleted = self.users.pop(index - 1)
        print(f"已删除用户: {deleted.get('name')} (ID: {deleted.get('id')})")
        return True
    
    def delete_by_id(self, user_id):
        """根据用户ID删除"""
        for idx, user in enumerate(self.users):
            if user.get('id') == user_id:
                deleted = self.users.pop(idx)
                print(f"已删除用户: {deleted.get('name')} (ID: {deleted.get('id')})")
                return True
        
        print(f"未找到用户ID: {user_id}")
        return False
    
    def delete_by_name(self, name):
        """根据姓名删除（删除所有同名用户）"""
        deleted_count = 0
        self.users = [u for u in self.users if u.get('name') != name or (deleted_count := deleted_count + 1, False)[1]]
        
        # 正确实现
        remaining = []
        for user in self.users:
            if user.get('name') == name:
                deleted_count += 1
                print(f"删除: {user.get('name')} (ID: {user.get('id')})")
            else:
                remaining.append(user)
        
        self.users = remaining
        
        if deleted_count > 0:
            print(f"共删除 {deleted_count} 个名为 {name} 的用户")
            return True
        else:
            print(f"未找到名为 {name} 的用户")
            return False
    
    def save(self):
        """保存到数据库文件"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
        
        print(f"已保存到 {self.db_path}")
        print(f"当前用户数: {len(self.users)}")


def main():
    """交互式用户管理"""
    manager = UserManager()
    
    while True:
        print("\n" + "="*60)
        print("用户管理菜单")
        print("="*60)
        print("1. 查看所有用户")
        print("2. 删除用户（按编号）")
        print("3. 删除用户（按ID）")
        print("4. 删除用户（按姓名）")
        print("5. 保存并退出")
        print("6. 退出不保存")
        print("="*60)
        
        choice = input("\n请选择操作 (1-6): ").strip()
        
        if choice == '1':
            manager.list_users()
        
        elif choice == '2':
            manager.list_users()
            try:
                idx = int(input("\n请输入要删除的用户编号: ").strip())
                if manager.delete_user(idx):
                    print("删除成功！记得选择\"5\"保存更改。")
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == '3':
            user_id = input("\n请输入用户ID: ").strip()
            if manager.delete_by_id(user_id):
                print("删除成功！记得选择\"5\"保存更改。")
        
        elif choice == '4':
            name = input("\n请输入用户姓名: ").strip()
            if manager.delete_by_name(name):
                print("删除成功！记得选择\"5\"保存更改。")
        
        elif choice == '5':
            manager.save()
            print("已保存，程序退出。")
            break
        
        elif choice == '6':
            print("退出不保存。")
            break
        
        else:
            print("无效选择，请重新输入")


if __name__ == '__main__':
    main()
