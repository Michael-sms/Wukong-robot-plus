# -*- coding: utf-8 -*-
"""
角色语音配置工具
用于快速添加和管理角色语音配置
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot import CharacterVoice, logging

logger = logging.getLogger(__name__)

def show_edge_voices():
    """显示所有可用的 Edge-TTS 音色"""
    print("\n" + "="*60)
    print("Edge-TTS 可用音色列表")
    print("="*60)
    
    voices = CharacterVoice.EDGE_TTS_VOICES
    
    print("\n【女声】")
    for name, code in voices.items():
        if "Xiao" in code:
            print(f"  {name:8s} - {code}")
    
    print("\n【男声】")
    for name, code in voices.items():
        if "Yun" in code:
            print(f"  {name:8s} - {code}")
    
    print("\n" + "="*60)


def show_current_config():
    """显示当前配置的角色"""
    print("\n" + "="*60)
    print("当前已配置的角色语音")
    print("="*60)
    
    char_map = CharacterVoice.CHARACTER_VOICE_MAP
    
    if not char_map:
        print("\n  还没有配置任何角色")
    else:
        for idx, (char, config) in enumerate(char_map.items(), 1):
            engine = config.get('engine', 'unknown')
            desc = config.get('description', '无描述')
            
            print(f"\n{idx}. 角色: {char}")
            print(f"   引擎: {engine}")
            print(f"   描述: {desc}")
            
            if engine == 'edge-tts':
                voice = config.get('voice', '')
                print(f"   音色: {voice}")
            elif engine == 'vits':
                url = config.get('server_url', '')
                speaker = config.get('speaker_id', 0)
                print(f"   服务: {url}")
                print(f"   说话人ID: {speaker}")
    
    print("\n" + "="*60)


def add_edge_character():
    """交互式添加 Edge-TTS 角色"""
    print("\n" + "="*60)
    print("添加 Edge-TTS 角色配置")
    print("="*60)
    
    char_name = input("\n请输入角色名称（如：千早爱音）: ").strip()
    
    if not char_name:
        print("角色名称不能为空")
        return
    
    print("\n请选择音色类型：")
    print("1. 从预设列表选择（推荐）")
    print("2. 手动输入音色代码")
    
    choice = input("\n请选择 (1-2): ").strip()
    
    if choice == '1':
        # 显示音色列表
        voices = CharacterVoice.EDGE_TTS_VOICES
        print("\n可选音色：")
        voice_list = list(voices.items())
        for idx, (name, code) in enumerate(voice_list, 1):
            print(f"{idx:2d}. {name:8s} - {code}")
        
        try:
            voice_idx = int(input("\n请选择音色编号: ").strip())
            if 1 <= voice_idx <= len(voice_list):
                voice_name, voice_code = voice_list[voice_idx - 1]
            else:
                print("编号无效")
                return
        except ValueError:
            print("请输入有效数字")
            return
    
    elif choice == '2':
        voice_code = input("\n请输入音色代码（如：zh-CN-XiaoxiaoNeural）: ").strip()
        if not voice_code:
            print("音色代码不能为空")
            return
        voice_name = "自定义"
    
    else:
        print("无效选择")
        return
    
    desc = input(f"\n请输入描述（如：温柔的少女音）[可选]: ").strip()
    if not desc:
        desc = f"使用 {voice_name} 音色"
    
    # 添加到配置
    CharacterVoice.add_character_voice(
        char_name,
        engine='edge-tts',
        voice=voice_code,
        description=desc
    )
    
    print(f"\n✓ 成功添加角色配置:")
    print(f"  角色: {char_name}")
    print(f"  音色: {voice_code}")
    print(f"  描述: {desc}")
    print("\n注意：此配置仅在本次运行有效")
    print("要永久保存，请编辑 robot/CharacterVoice.py 文件")


def test_voice():
    """测试当前配置"""
    import subprocess
    
    print("\n" + "="*60)
    print("测试 Edge-TTS 语音")
    print("="*60)
    
    show_current_config()
    
    char_name = input("\n请输入要测试的角色名称: ").strip()
    
    if not char_name:
        print("角色名称不能为空")
        return
    
    voice_config = CharacterVoice.get_character_voice(char_name)
    
    if voice_config.get('engine') != 'edge-tts':
        print(f"角色 '{char_name}' 不是 Edge-TTS 引擎，无法测试")
        return
    
    voice = voice_config.get('voice')
    test_text = input(f"\n请输入测试文本（默认：你好，我是{char_name}）: ").strip()
    
    if not test_text:
        test_text = f"你好，我是{char_name}"
    
    print(f"\n正在生成语音...")
    print(f"音色: {voice}")
    print(f"文本: {test_text}")
    
    try:
        output_file = "temp/test_voice.mp3"
        os.makedirs("temp", exist_ok=True)
        
        # 调用 edge-tts 命令行
        cmd = f'edge-tts --voice "{voice}" --text "{test_text}" --write-media "{output_file}"'
        subprocess.run(cmd, shell=True, check=True)
        
        print(f"\n✓ 语音生成成功: {output_file}")
        print("请使用播放器播放该文件")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")


def main():
    """主菜单"""
    while True:
        print("\n" + "="*60)
        print("角色语音配置工具")
        print("="*60)
        print("1. 查看可用的 Edge-TTS 音色")
        print("2. 查看当前角色配置")
        print("3. 添加新角色（Edge-TTS）")
        print("4. 测试角色语音")
        print("5. 退出")
        print("="*60)
        
        choice = input("\n请选择操作 (1-5): ").strip()
        
        if choice == '1':
            show_edge_voices()
        
        elif choice == '2':
            show_current_config()
        
        elif choice == '3':
            add_edge_character()
        
        elif choice == '4':
            test_voice()
        
        elif choice == '5':
            print("\n再见！")
            break
        
        else:
            print("\n无效选择，请重试")


if __name__ == '__main__':
    main()
