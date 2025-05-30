#!/usr/bin/env python3
"""
测试文字反馈区域滚动功能的脚本
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_ui import feedback_ui

def test_scroll_functionality():
    """测试滚动功能"""
    
    # 创建一个很长的测试文本
    long_text = """这是一个测试滚动功能的长文本。
我们需要确保当文本内容超过文字反馈区域的可视高度时，
能够正确显示滚动条并且可以使用鼠标滚轮进行滚动。

这里是第5行文本。
这里是第6行文本。
这里是第7行文本。
这里是第8行文本。
这里是第9行文本。
这里是第10行文本。
这里是第11行文本。
这里是第12行文本。
这里是第13行文本。
这里是第14行文本。
这里是第15行文本。
这里是第16行文本 - 应该需要滚动才能看到。
这里是第17行文本 - 应该需要滚动才能看到。
这里是第18行文本 - 应该需要滚动才能看到。
这里是第19行文本 - 应该需要滚动才能看到。
这里是第20行文本 - 应该需要滚动才能看到。

请测试以下功能：
1. 垂直滚动条是否显示
2. 鼠标滚轮是否可以滚动
3. 点击滚动条是否可以滚动
4. 滚动条的样式是否美观

如果以上功能都正常，说明滚动修复成功！"""
    
    print("🧪 启动滚动功能测试...")
    print("📝 将显示一个包含长文本的反馈界面")
    print("🔍 请测试以下功能：")
    print("   1. 垂直滚动条是否显示")
    print("   2. 鼠标滚轮是否可以滚动")
    print("   3. 点击滚动条是否可以滚动")
    print("   4. 滚动条的样式是否美观")
    print()
    
    # 启动反馈界面进行测试
    result = feedback_ui(
        project_directory=os.getcwd(),
        prompt=long_text,
        dark_theme=True
    )
    
    if result:
        print("✅ 测试完成")
        print(f"📄 反馈内容: {result['interactive_feedback']}")
    else:
        print("❌ 测试被取消")

if __name__ == "__main__":
    test_scroll_functionality() 