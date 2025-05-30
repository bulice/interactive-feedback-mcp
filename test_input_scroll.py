#!/usr/bin/env python3
"""
测试用户输入时的滚动功能
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_ui import feedback_ui

def test_input_scroll():
    """测试用户输入时的滚动功能"""
    
    prompt = """请在下方的文字反馈区域输入多行文本来测试滚动功能。

测试步骤：
1. 在"您的文字反馈"区域输入文字
2. 输入超过8行文本
3. 观察是否出现垂直滚动条
4. 测试鼠标滚轮是否可以滚动

请输入足够多的文字来触发滚动条显示。"""
    
    print("🧪 启动用户输入滚动测试...")
    print("📝 请在反馈区域输入多行文本来测试滚动功能")
    print("🔍 输入超过8行文本应该会显示滚动条")
    print()
    
    # 启动反馈界面进行测试
    result = feedback_ui(
        project_directory=os.getcwd(),
        prompt=prompt,
        dark_theme=True
    )
    
    if result:
        print("✅ 测试完成")
        feedback_data = result['interactive_feedback']
        print(f"📄 用户输入的反馈长度: {len(feedback_data)} 字符")
        if len(feedback_data) > 200:
            print("✅ 输入了足够长的文本，滚动功能应该已被测试")
        else:
            print("⚠️  输入文本较短，可能未触发滚动条")
    else:
        print("❌ 测试被取消")

if __name__ == "__main__":
    test_input_scroll() 