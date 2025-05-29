"""
交互式反馈收集器 MCP 服务器
AI调用时会汇报工作内容，用户可以提供文本反馈和/或图片反馈
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP(
    "交互式反馈收集器",
    dependencies=["PySide6", "pillow"]
)


@mcp.tool()
def interactive_feedback(project_directory: str = "", summary: str = "", theme: str = "light") -> str:
    """
    启动交互式反馈界面，收集用户的文字和图片反馈。
    使用PySide6界面，支持明亮和暗黑主题。
    
    Args:
        project_directory: 项目目录路径，默认为当前工作目录
        summary: AI工作汇报内容
        theme: 界面主题，'light'(明亮)或'dark'(暗黑)，默认明亮主题
        
    Returns:
        包含用户反馈内容的JSON字符串
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
                    feedback_data = json.load(f)
                    
                # 清理临时文件
                os.unlink(temp_output)
                
                # 返回反馈数据
                return json.dumps(feedback_data, ensure_ascii=False, indent=2)
            else:
                # 如果没有输出文件，表示用户可能取消了
                return json.dumps({
                    "command_logs": "",
                    "interactive_feedback": json.dumps({
                        "text_feedback": "",
                        "images": []
                    }, ensure_ascii=False)
                }, ensure_ascii=False, indent=2)
                
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
        return json.dumps({
            "error": f"interactive_feedback工具执行失败: {str(e)}",
            "command_logs": "",
            "interactive_feedback": json.dumps({
                "text_feedback": "",
                "images": []
            }, ensure_ascii=False)
        }, ensure_ascii=False, indent=2)


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