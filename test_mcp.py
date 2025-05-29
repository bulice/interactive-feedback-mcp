#!/usr/bin/env python3
"""
测试MCP服务器连接的简单脚本
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """测试MCP服务器是否能正确响应协议消息"""
    
    print("🔍 正在启动MCP服务器进行测试...", file=sys.stderr)
    
    # 启动服务器进程
    process = subprocess.Popen(
        ["/Users/lee/.local/bin/uv", "run", "server.py"],
        cwd="/Users/lee/tmp/interactive-feedback-mcp",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # 发送初始化消息
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 发送初始化消息...", file=sys.stderr)
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        # 等待响应
        print("⏳ 等待服务器响应...", file=sys.stderr)
        
        # 设置超时
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ 服务器进程正在运行", file=sys.stderr)
            
            # 尝试读取响应
            try:
                response = process.stdout.readline()
                if response:
                    print(f"📥 收到响应: {response.strip()}", file=sys.stderr)
                else:
                    print("⚠️  没有收到响应", file=sys.stderr)
            except Exception as e:
                print(f"❌ 读取响应时出错: {e}", file=sys.stderr)
        else:
            print(f"❌ 服务器进程已退出，退出码: {process.poll()}", file=sys.stderr)
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"错误输出: {stderr_output}", file=sys.stderr)
    
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}", file=sys.stderr)
    
    finally:
        # 清理进程
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    test_mcp_server() 