#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wukong-robot 插件生成器
交互式创建插件模板，快速开发新技能

使用方法：
    python3 tools/plugin_generator.py
"""

import os
import re
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot import constants


class PluginGenerator:
    """插件生成器"""
    
    TEMPLATE_SIMPLE = """# -*- coding: utf-8 -*-
# 插件名: {plugin_name}
# 作者: {author}
# 描述: {description}

import logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    
    SLUG = "{slug}"
    
    def handle(self, text, parsed):
        \"\"\"
        处理用户指令
        
        参数:
            text: 用户说的话（字符串）
            parsed: NLU 解析结果
        \"\"\"
        logger.info(f"{{self.SLUG}} 插件被触发，用户说: {{text}}")
        
        # TODO: 在这里实现你的插件逻辑
        self.say("收到指令：{{}}".format(text), cache=True)
    
    def isValid(self, text, parsed):
        \"\"\"
        判断该插件是否适合处理当前指令
        
        参数:
            text: 用户说的话（字符串）
            parsed: NLU 解析结果
            
        返回:
            bool: True 表示该插件可以处理
        \"\"\"
        # 简单关键词匹配
        return any(word in text for word in {keywords})
"""

    TEMPLATE_NLU = """# -*- coding: utf-8 -*-
# 插件名: {plugin_name}
# 作者: {author}
# 描述: {description}

import logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    
    SLUG = "{slug}"
    
    def handle(self, text, parsed):
        \"\"\"
        处理用户指令
        
        参数:
            text: 用户说的话（字符串）
            parsed: NLU 解析结果
        \"\"\"
        logger.info(f"{{self.SLUG}} 插件被触发")
        
        # 检查是否有意图
        if self.nlu.hasIntent(parsed, "{intent_name}"):
            # 提取槽位信息
            slots = self.nlu.getSlots(parsed, "{intent_name}")
            
            # TODO: 根据槽位信息执行相应操作
            for slot in slots:
                slot_name = slot.get("name")
                slot_value = slot.get("normalized_word", slot.get("word"))
                logger.info(f"槽位: {{slot_name}} = {{slot_value}}")
            
            self.say("好的，正在处理您的请求", cache=True)
        else:
            self.say("抱歉，我没有理解您的意思", cache=True)
    
    def isValid(self, text, parsed):
        \"\"\"
        判断该插件是否适合处理当前指令
        
        使用 NLU 意图识别判断
        \"\"\"
        return self.nlu.hasIntent(parsed, "{intent_name}")
"""

    TEMPLATE_IMMERSIVE = """# -*- coding: utf-8 -*-
# 插件名: {plugin_name}
# 作者: {author}
# 描述: {description}

import logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    
    SLUG = "{slug}"
    IS_IMMERSIVE = True  # 沉浸式插件
    
    def handle(self, text, parsed):
        \"\"\"
        处理用户指令（沉浸式模式）
        
        沉浸式插件会接管对话，直到用户主动退出
        \"\"\"
        logger.info(f"{{self.SLUG}} 沉浸式插件启动")
        
        self.say("进入{plugin_name}模式，说"退出"可以结束", cache=True)
        
        # 主循环
        while True:
            query = self.activeListen()
            query = query.strip()
            
            if not query:
                continue
                
            # 退出条件
            if any(word in query for word in ["退出", "结束", "停止"]):
                self.say("好的，退出{plugin_name}模式", cache=True)
                self.clearImmersive()
                break
            
            # TODO: 处理用户在沉浸式模式下的输入
            logger.info(f"沉浸式模式收到: {{query}}")
            self.say(f"您说：{{query}}", cache=True)
    
    def isValid(self, text, parsed):
        \"\"\"
        判断该插件是否适合处理当前指令
        \"\"\"
        return any(word in text for word in {keywords})
"""

    def __init__(self):
        self.plugin_dir = constants.PLUGIN_PATH
        
    def input_with_default(self, prompt, default=""):
        """带默认值的输入"""
        if default:
            result = input(f"{prompt} [{default}]: ").strip()
            return result if result else default
        else:
            return input(f"{prompt}: ").strip()
    
    def validate_slug(self, slug):
        """验证 SLUG 格式"""
        if not slug:
            return False
        # SLUG 只能包含字母、数字和下划线
        if not re.match(r'^[a-z][a-z0-9_]*$', slug):
            return False
        # 检查是否已存在
        plugin_file = os.path.join(self.plugin_dir, f"{slug.capitalize()}.py")
        if os.path.exists(plugin_file):
            print(f"⚠️  警告：插件文件 {slug.capitalize()}.py 已存在！")
            return False
        return True
    
    def collect_info(self):
        """收集插件信息"""
        print("\n" + "="*60)
        print("🚀 wukong-robot 插件生成器")
        print("="*60 + "\n")
        
        # 插件名称
        while True:
            plugin_name = self.input_with_default("插件名称（中文）", "我的插件")
            if plugin_name:
                break
            print("❌ 插件名称不能为空\n")
        
        # SLUG
        while True:
            default_slug = re.sub(r'[^a-z0-9]', '', plugin_name.lower())
            if not default_slug:
                default_slug = "myplugin"
            slug = self.input_with_default("插件 SLUG（英文标识，小写字母）", default_slug)
            if self.validate_slug(slug):
                break
            print("❌ SLUG 格式错误或已存在，请重新输入\n")
        
        # 作者
        author = self.input_with_default("作者", os.getenv("USER", "Developer"))
        
        # 描述
        description = self.input_with_default("插件描述", f"{plugin_name}技能插件")
        
        # 插件类型
        print("\n选择插件类型：")
        print("  1. 简单插件（关键词匹配）")
        print("  2. NLU 插件（使用意图识别）")
        print("  3. 沉浸式插件（接管对话流程）")
        
        while True:
            plugin_type = self.input_with_default("请选择", "1")
            if plugin_type in ["1", "2", "3"]:
                plugin_type = int(plugin_type)
                break
            print("❌ 请输入 1、2 或 3\n")
        
        # 根据类型收集额外信息
        keywords = []
        intent_name = ""
        
        if plugin_type in [1, 3]:
            # 关键词
            keywords_input = self.input_with_default(
                "触发关键词（多个用逗号分隔）",
                plugin_name
            )
            keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        
        if plugin_type == 2:
            # NLU 意图名
            intent_name = self.input_with_default(
                "NLU 意图名称（大写，如：PLAY_MUSIC）",
                "CUSTOM_INTENT"
            ).upper()
        
        return {
            "plugin_name": plugin_name,
            "slug": slug,
            "author": author,
            "description": description,
            "plugin_type": plugin_type,
            "keywords": keywords,
            "intent_name": intent_name
        }
    
    def generate(self, info):
        """生成插件文件"""
        # 选择模板
        if info["plugin_type"] == 1:
            template = self.TEMPLATE_SIMPLE
        elif info["plugin_type"] == 2:
            template = self.TEMPLATE_NLU
        else:
            template = self.TEMPLATE_IMMERSIVE
        
        # 填充模板
        code = template.format(
            plugin_name=info["plugin_name"],
            slug=info["slug"],
            author=info["author"],
            description=info["description"],
            keywords=info["keywords"],
            intent_name=info.get("intent_name", "")
        )
        
        # 文件名：首字母大写
        filename = info["slug"].capitalize() + ".py"
        filepath = os.path.join(self.plugin_dir, filename)
        
        # 写入文件
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            return filepath
        except Exception as e:
            print(f"❌ 写入文件失败: {e}")
            return None
    
    def show_summary(self, info, filepath):
        """显示生成摘要"""
        print("\n" + "="*60)
        print("✅ 插件生成成功！")
        print("="*60)
        print(f"📝 插件名称: {info['plugin_name']}")
        print(f"🔖 SLUG: {info['slug']}")
        print(f"👤 作者: {info['author']}")
        print(f"📄 文件路径: {filepath}")
        print(f"📦 类型: ", end="")
        
        type_names = {1: "简单插件", 2: "NLU插件", 3: "沉浸式插件"}
        print(type_names[info['plugin_type']])
        
        if info['keywords']:
            print(f"🔑 触发关键词: {', '.join(info['keywords'])}")
        
        if info.get('intent_name'):
            print(f"🎯 NLU 意图: {info['intent_name']}")
        
        print("\n📚 后续步骤：")
        print(f"  1. 编辑插件文件：{filepath}")
        print("  2. 实现 handle() 方法中的 TODO 部分")
        
        if info['plugin_type'] == 2:
            print(f"  3. 在百度 UNIT 中配置意图：{info['intent_name']}")
            print("  4. 配置槽位和训练数据")
        
        print("  5. 重启 wukong-robot 测试插件")
        print("\n🎉 开始开发你的插件吧！\n")
    
    def run(self):
        """运行生成器"""
        try:
            info = self.collect_info()
            
            # 确认生成
            print("\n" + "-"*60)
            print("📋 插件信息确认：")
            print(f"  名称: {info['plugin_name']}")
            print(f"  SLUG: {info['slug']}")
            print(f"  作者: {info['author']}")
            print("-"*60)
            
            confirm = self.input_with_default("\n确认生成？(y/n)", "y")
            if confirm.lower() not in ["y", "yes", "是"]:
                print("❌ 已取消")
                return
            
            # 生成插件
            filepath = self.generate(info)
            
            if filepath:
                self.show_summary(info, filepath)
            else:
                print("❌ 生成失败")
                
        except KeyboardInterrupt:
            print("\n\n❌ 已取消")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    generator = PluginGenerator()
    generator.run()


if __name__ == "__main__":
    main()
