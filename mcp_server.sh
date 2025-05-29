#!/bin/bash

# MCP Server启动脚本
# 确保正确的工作目录和环境

set -e

# 创建日志目录
LOG_DIR="/Users/lee/tmp/interactive-feedback-mcp/logs"
mkdir -p "$LOG_DIR"

# 日志文件
LOG_FILE="$LOG_DIR/mcp_server.log"
ERROR_LOG="$LOG_DIR/mcp_error.log"

# 记录启动时间
echo "$(date): MCP Server starting..." >> "$LOG_FILE"

# 切换到项目目录
cd /Users/lee/tmp/interactive-feedback-mcp

# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONPATH="/Users/lee/tmp/interactive-feedback-mcp:$PYTHONPATH"

# 记录环境信息
echo "$(date): Working directory: $(pwd)" >> "$LOG_FILE"
echo "$(date): Python path: $PYTHONPATH" >> "$LOG_FILE"
echo "$(date): UV path: /Users/lee/.local/bin/uv" >> "$LOG_FILE"

# 启动服务器，重定向日志
exec /Users/lee/.local/bin/uv run server.py 2>> "$ERROR_LOG" | tee -a "$LOG_FILE" 