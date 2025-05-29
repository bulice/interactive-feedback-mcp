#!/usr/bin/env python3
"""
MCP连接问题诊断工具
"""

import json
import subprocess
import sys
import time
import os
from pathlib import Path

def check_file_permissions():
    """检查文件权限"""
    print("🔍 检查文件权限...")
    script_path = Path("mcp_server.sh")
    if script_path.exists():
        stat = script_path.stat()
        print(f"  ✅ mcp_server.sh 权限: {oct(stat.st_mode)[-3:]}")
        return stat.st_mode & 0o111 != 0  # 检查是否有执行权限
    else:
        print("  ❌ mcp_server.sh 不存在")
        return False

def check_uv_path():
    """检查uv路径"""
    print("🔍 检查uv路径...")
    uv_path = Path("/Users/lee/.local/bin/uv")
    if uv_path.exists():
        print(f"  ✅ UV存在: {uv_path}")
        return True
    else:
        print(f"  ❌ UV不存在: {uv_path}")
        return False

def test_script_execution():
    """测试启动脚本执行"""
    print("🔍 测试启动脚本执行...")
    try:
        process = subprocess.Popen(
            ["./mcp_server.sh"],
            cwd="/Users/lee/tmp/interactive-feedback-mcp",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待一小段时间
        time.sleep(3)
        
        if process.poll() is None:
            print("  ✅ 脚本正在运行")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            print(f"  ❌ 脚本退出，退出码: {process.poll()}")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"  标准输出: {stdout}")
            if stderr:
                print(f"  错误输出: {stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 执行脚本时出错: {e}")
        return False

def test_mcp_protocol():
    """测试MCP协议通信"""
    print("🔍 测试MCP协议通信...")
    try:
        process = subprocess.Popen(
            ["/Users/lee/.local/bin/uv", "run", "server.py"],
            cwd="/Users/lee/tmp/interactive-feedback-mcp",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 发送初始化消息
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        # 等待响应
        time.sleep(2)
        
        success = False
        if process.poll() is None:
            try:
                response = process.stdout.readline()
                if response and "result" in response:
                    print("  ✅ MCP协议响应正常")
                    success = True
                else:
                    print("  ⚠️  MCP协议无响应或响应异常")
            except Exception as e:
                print(f"  ❌ 读取MCP响应时出错: {e}")
        else:
            print(f"  ❌ MCP服务器进程已退出: {process.poll()}")
        
        # 清理
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        return success
        
    except Exception as e:
        print(f"  ❌ MCP协议测试出错: {e}")
        return False

def generate_cursor_config():
    """生成Cursor配置建议"""
    print("📝 生成Cursor配置建议...")
    
    configs = [
        {
            "name": "方案1: 使用启动脚本",
            "config": {
                "command": "/Users/lee/tmp/interactive-feedback-mcp/mcp_server.sh",
                "args": [],
                "timeout": 600,
                "autoApprove": ["interactive_feedback"]
            }
        },
        {
            "name": "方案2: 直接使用uv",
            "config": {
                "command": "/Users/lee/.local/bin/uv",
                "args": ["--directory", "/Users/lee/tmp/interactive-feedback-mcp", "run", "server.py"],
                "timeout": 600,
                "autoApprove": ["interactive_feedback"]
            }
        },
        {
            "name": "方案3: 使用Python直接运行",
            "config": {
                "command": "/Users/lee/tmp/interactive-feedback-mcp/.venv/bin/python",
                "args": ["server.py"],
                "cwd": "/Users/lee/tmp/interactive-feedback-mcp",
                "timeout": 600,
                "autoApprove": ["interactive_feedback"]
            }
        }
    ]
    
    for i, config_option in enumerate(configs, 1):
        print(f"\n  {config_option['name']}:")
        config_json = {
            "mcpServers": {
                "interactive-feedback-mcp": config_option['config']
            }
        }
        print(f"  {json.dumps(config_json, indent=2, ensure_ascii=False)}")

def main():
    """主函数"""
    print("🚀 MCP连接问题诊断工具")
    print("=" * 50)
    
    # 执行各项检查
    checks = [
        ("文件权限", check_file_permissions),
        ("UV路径", check_uv_path),
        ("脚本执行", test_script_execution),
        ("MCP协议", test_mcp_protocol)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n{'='*20} {name} {'='*20}")
        results[name] = check_func()
    
    # 总结
    print(f"\n{'='*20} 诊断总结 {'='*20}")
    all_passed = True
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查都通过了！")
        print("如果Cursor仍然连接失败，请尝试以下步骤：")
        print("1. 完全重启Cursor")
        print("2. 等待10-15秒让MCP服务器初始化")
        print("3. 检查Cursor的MCP日志")
    else:
        print("\n⚠️  发现问题，请按照上述错误信息进行修复")
    
    # 生成配置建议
    print(f"\n{'='*20} 配置建议 {'='*20}")
    generate_cursor_config()

if __name__ == "__main__":
    main() 