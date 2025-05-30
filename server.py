"""
交互式反馈收集器 MCP 服务器
AI调用时会汇报工作内容，用户可以提供文本反馈和/或图片反馈
"""

import os
import sys
import subprocess
import tempfile
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent

# 创建MCP服务器
mcp = FastMCP(
    "交互式反馈收集器",
    dependencies=["PySide6", "pillow"]
)


@mcp.tool()
def interactive_feedback(project_directory: str = "", summary: str = "", theme: str = "light") -> List[Union[TextContent, ImageContent]]:
    """
    启动交互式反馈界面，收集用户的文字和图片反馈。
    使用PySide6界面，支持明亮和暗黑主题。
    
    Args:
        project_directory: 项目目录路径，默认为当前工作目录
        summary: AI工作汇报内容
        theme: 界面主题，'light'(明亮)或'dark'(暗黑)，默认明亮主题
        
    Returns:
        包含用户反馈内容的列表，可能包含文本和图片内容对象
    """
    try:
        # 如果没有指定项目目录，使用当前工作目录
        if not project_directory:
            project_directory = os.getcwd()
        
        # 确保项目目录存在
        if not os.path.exists(project_directory):
            project_directory = os.getcwd()
            
        # 验证主题参数
        if theme not in ['light', 'dark']:
            theme = 'light'
            
        # 构建命令
        script_path = os.path.join(os.path.dirname(__file__), 'feedback_ui.py')
        cmd = [
            sys.executable, script_path,
            '--project-directory', project_directory,
            '--prompt', summary or "AI助手工作完成，请提供反馈。",
            '--theme', theme
        ]
        
        # 创建临时文件保存结果
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_output = temp_file.name
            cmd.extend(['--output-file', temp_output])
        
        try:
            # 运行反馈界面
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # 检查是否成功创建了输出文件
            if os.path.exists(temp_output):
                with open(temp_output, 'r', encoding='utf-8') as f:
                    feedback_result = json.load(f)
                    
                # 清理临时文件
                os.unlink(temp_output)
                
                # 解析反馈内容
                interactive_feedback_str = feedback_result.get('interactive_feedback', '{}')
                try:
                    feedback_data = json.loads(interactive_feedback_str)
                except json.JSONDecodeError:
                    feedback_data = {}
                
                # 构建返回内容列表
                feedback_items = []
                
                # 获取当前时间戳
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 添加文字反馈
                text_feedback = feedback_data.get('text_feedback', '').strip()
                if text_feedback:
                    feedback_items.append(TextContent(
                        type="text",
                        text=f"用户文字反馈：{text_feedback}\n提交时间：{timestamp}"
                    ))
                
                # 添加图片反馈
                images = feedback_data.get('images', [])
                if images:
                    for image_path in images:
                        try:
                            if os.path.exists(image_path):
                                # 读取图片文件
                                with open(image_path, 'rb') as img_file:
                                    image_data = img_file.read()
                                
                                # 将图片数据编码为 base64
                                base64_data = base64.b64encode(image_data).decode('utf-8')
                                
                                # 根据文件扩展名确定格式
                                file_ext = Path(image_path).suffix.lower()
                                if file_ext in ['.jpg', '.jpeg']:
                                    media_type = 'image/jpeg'
                                elif file_ext == '.png':
                                    media_type = 'image/png'
                                elif file_ext == '.gif':
                                    media_type = 'image/gif'
                                elif file_ext in ['.bmp']:
                                    media_type = 'image/bmp'
                                else:
                                    media_type = 'image/png'  # 默认为 PNG
                                
                                feedback_items.append(ImageContent(
                                    type="image",
                                    data=base64_data,
                                    mimeType=media_type
                                ))
                                
                        except Exception as e:
                            # 如果图片读取失败，添加错误信息
                            feedback_items.append(TextContent(
                                type="text",
                                text=f"图片加载失败 ({os.path.basename(image_path)}): {str(e)}"
                            ))
                
                # 如果没有任何反馈内容，添加默认信息
                if not feedback_items:
                    feedback_items.append(TextContent(
                        type="text",
                        text=f"用户未提供反馈内容\n提交时间：{timestamp}"
                    ))
                
                return feedback_items
            else:
                # 如果没有输出文件，表示用户可能取消了
                return []
                
        except subprocess.TimeoutExpired:
            # 清理临时文件
            if os.path.exists(temp_output):
                os.unlink(temp_output)
            raise Exception("反馈界面超时（10分钟）")
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_output):
                os.unlink(temp_output)
            raise Exception(f"启动反馈界面失败: {str(e)}")
            
    except Exception as e:
        return []


@mcp.tool()
def get_image_info(image_path: str) -> str:
    """
    获取指定路径图片的信息（尺寸、格式等）
    
    Args:
        image_path: 图片文件路径
    """
    try:
        from PIL import Image
        path = Path(image_path)
        if not path.exists():
            return f"文件不存在: {image_path}"
            
        with Image.open(path) as img:
            info = {
                "文件名": path.name,
                "格式": img.format,
                "尺寸": f"{img.width} x {img.height}",
                "模式": img.mode,
                "文件大小": f"{path.stat().st_size / 1024:.1f} KB"
            }
            
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
        
    except Exception as e:
        return f"获取图片信息失败: {str(e)}"


if __name__ == "__main__":
    # 添加调试信息
    print(f"Starting MCP server: {mcp.name}", file=sys.stderr)
    print("Waiting for MCP client connection...", file=sys.stderr)
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("Server interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the mcp-feedback-collector command."""
    print(f"Starting MCP server: {mcp.name}", file=sys.stderr)
    print("Waiting for MCP client connection...", file=sys.stderr)
        
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("Server interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1) 