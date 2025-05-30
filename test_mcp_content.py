#!/usr/bin/env python3
"""
测试新的 MCP 内容对象返回格式
"""

import sys
import os
import json
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feedback_ui import feedback_ui

def test_mcp_content():
    """测试 MCP 内容对象格式"""
    
    prompt = """🧪 测试新的 MCP 内容对象格式

这个测试将验证反馈系统现在返回标准的 MCP 内容对象：

## 新功能：

1. **标准的 MCP 内容对象**：
   - TextContent 对象包含文字反馈
   - ImageContent 对象包含图片二进制数据

2. **时间戳信息**：
   - 每个文字反馈都会包含提交时间戳

3. **图片二进制数据**：
   - 图片不再是文件路径，而是 base64 编码的二进制数据
   - 支持 JPEG、PNG、GIF、BMP 等格式

## 测试步骤：

1. **输入文字反馈**：在下方输入框中输入一些测试文字

2. **添加图片**（可选）：
   - 选择本地图片文件，或
   - 粘贴剪贴板中的图片

3. **提交反馈**：点击提交按钮

4. **查看返回数据**：检查返回的 MCP 内容对象格式

## 预期结果：

返回的数据应该是标准的 MCP 内容对象列表，包含：
- TextContent 对象（如果有文字反馈）
- ImageContent 对象（如果有图片反馈）
- 时间戳信息

请测试并确认新格式是否符合预期！"""
    
    print("🧪 启动 MCP 内容对象格式测试...")
    print("📝 请输入文字反馈和/或添加图片")
    print("⏰ 新格式包含时间戳和图片二进制数据")
    print()
    
    # 启动反馈界面进行测试
    result = feedback_ui(
        project_directory=os.getcwd(),
        prompt=prompt,
        dark_theme=True
    )
    
    if result:
        print("✅ 反馈收集完成")
        print("\n📊 返回数据分析：")
        
        # 解析 interactive_feedback
        feedback_data = json.loads(result['interactive_feedback'])
        print(f"💬 文字反馈: {feedback_data.get('text_feedback', '无')}")
        
        images = feedback_data.get('images', [])
        if images:
            print(f"🖼️  图片数量: {len(images)}")
            for i, image_path in enumerate(images):
                print(f"   图片 {i+1}: {os.path.basename(image_path)}")
                # 检查文件是否存在
                if os.path.exists(image_path):
                    size = os.path.getsize(image_path)
                    print(f"   📏 文件大小: {size} 字节")
                else:
                    print(f"   ❌ 文件不存在")
        else:
            print("📷 没有选择图片")
            
        print("\n🔗 模拟 MCP 内容对象转换...")
        
        # 模拟 server.py 中的转换逻辑
        from datetime import datetime
        import base64
        
        feedback_items = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 处理文字反馈
        text_feedback = feedback_data.get('text_feedback', '').strip()
        if text_feedback:
            text_content = {
                "type": "text",
                "text": f"用户文字反馈：{text_feedback}\n提交时间：{timestamp}"
            }
            feedback_items.append(text_content)
            print(f"✅ TextContent 对象已创建")
        
        # 处理图片反馈
        for image_path in images:
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as img_file:
                        image_data = img_file.read()
                    
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    file_ext = Path(image_path).suffix.lower()
                    
                    if file_ext in ['.jpg', '.jpeg']:
                        media_type = 'image/jpeg'
                    elif file_ext == '.png':
                        media_type = 'image/png'
                    else:
                        media_type = 'image/png'
                    
                    image_content = {
                        "type": "image",
                        "data": base64_data[:50] + "...(截断)",  # 只显示前50个字符
                        "mimeType": media_type
                    }
                    feedback_items.append(image_content)
                    print(f"✅ ImageContent 对象已创建 ({media_type})")
                    
                except Exception as e:
                    print(f"❌ 图片处理失败: {e}")
        
        print(f"\n📋 最终 MCP 内容对象数量: {len(feedback_items)}")
        for i, item in enumerate(feedback_items):
            print(f"   {i+1}. {item['type']} 对象")
            
    else:
        print("❌ 测试被取消")

if __name__ == "__main__":
    test_mcp_content() 