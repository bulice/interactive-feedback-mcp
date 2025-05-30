#!/usr/bin/env python3
"""
测试图片粘贴功能和临时文件处理
"""

import sys
import os
import json

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_ui import feedback_ui

def test_image_paste():
    """测试图片粘贴功能"""
    
    prompt = """🖼️ 测试图片粘贴功能

## 测试步骤：

1. **复制图片到剪贴板**：
   - 从任何应用程序复制一张图片（如截图、浏览器中的图片等）
   - 或者使用系统截图工具（如 macOS 的 Cmd+Shift+4）

2. **粘贴图片**：
   - 点击"📋 粘贴图片"按钮
   - 图片应该显示在图片区域中
   - 控制台应该显示临时文件路径

3. **提交反馈**：
   - 输入一些文字反馈
   - 点击"✅ 提交反馈"
   - 检查返回的 JSON 中是否包含正确的图片路径

## 预期效果：

- 粘贴的图片应该正确显示
- 临时文件路径应该有效
- 提交反馈后，MCP 调用者应该能够访问图片文件
- 不应该出现"文件不存在"错误

请按照以上步骤测试图片粘贴功能！"""
    
    print("🧪 启动图片粘贴功能测试...")
    print("📋 请先复制一张图片到剪贴板，然后点击'粘贴图片'按钮")
    print("🖼️  测试图片是否能正确显示和保存")
    print()
    
    # 启动反馈界面进行测试
    result = feedback_ui(
        project_directory=os.getcwd(),
        prompt=prompt,
        dark_theme=True
    )
    
    if result:
        print("✅ 图片粘贴测试完成")
        feedback_data = json.loads(result['interactive_feedback'])
        print(f"📄 文字反馈: {feedback_data.get('text_feedback', '')}")
        
        images = feedback_data.get('images', [])
        if images:
            print(f"🖼️  图片数量: {len(images)}")
            for i, image_path in enumerate(images):
                print(f"   图片 {i+1}: {image_path}")
                # 检查文件是否存在
                if os.path.exists(image_path):
                    print(f"   ✅ 文件存在")
                    # 获取文件大小
                    size = os.path.getsize(image_path)
                    print(f"   📏 文件大小: {size} 字节")
                else:
                    print(f"   ❌ 文件不存在！")
        else:
            print("📷 没有选择图片")
    else:
        print("❌ 测试被取消")

if __name__ == "__main__":
    test_image_paste() 