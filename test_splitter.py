#!/usr/bin/env python3
"""
测试可拖拽分割器功能
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_ui import feedback_ui

def test_splitter():
    """测试可拖拽分割器功能"""
    
    prompt = """🎯 测试可拖拽分割器功能

这是一个较长的 AI 工作汇报内容，用于测试分割器功能。

## 测试步骤：

1. **查看分割线**：在 AI 工作汇报区域和用户输入区域之间应该有一条可拖拽的分割线

2. **拖拽测试**：
   - 将鼠标移动到分割线上，光标应该变成调整大小的样式
   - 按住鼠标左键并拖拽，可以调整两个区域的高度比例
   - 向上拖拽：增加 AI 工作汇报区域，减少用户输入区域
   - 向下拖拽：减少 AI 工作汇报区域，增加用户输入区域

3. **状态保存**：
   - 调整分割器位置后关闭窗口
   - 重新打开应该保持上次的分割位置

4. **滚动测试**：
   - 在 AI 工作汇报区域：如果内容超出显示范围，应该显示滚动条
   - 在用户输入区域：输入大量文字时应该显示滚动条

## 预期效果：

- 分割线应该清晰可见且易于拖拽
- 两个区域的高度可以自由调整
- 调整后的比例会被保存并在下次打开时恢复
- 每个区域都有独立的滚动条（如果需要）

请测试以上功能并提供反馈！"""
    
    print("🧪 启动可拖拽分割器测试...")
    print("📏 请测试 AI 工作汇报区域和用户输入区域之间的分割线")
    print("🖱️  拖拽分割线可以调整两个区域的高度比例")
    print("💾 调整后的位置会自动保存")
    print()
    
    # 启动反馈界面进行测试
    result = feedback_ui(
        project_directory=os.getcwd(),
        prompt=prompt,
        dark_theme=True
    )
    
    if result:
        print("✅ 分割器测试完成")
        feedback_data = result['interactive_feedback']
        print(f"📄 用户反馈: {feedback_data}")
    else:
        print("❌ 测试被取消")

if __name__ == "__main__":
    test_splitter() 