# Interactive Feedback MCP - 交互式反馈收集器

> 基于 Fábio Ferreira ([@fabiomlferreira](https://x.com/fabiomlferreira)) 的原始项目进行二次开发  
> 参考项目：[sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)  
> 当前维护者：bulice  
> 更多 AI 开发增强工具请访问 [dotcursorrules.com](https://dotcursorrules.com/)

## 📖 项目概述

Interactive Feedback MCP 是一个基于 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 的服务器，专为 AI 辅助开发工具（如 [Cursor](https://www.cursor.com)、[Cline](https://cline.bot)、[Windsurf](https://windsurf.com)）设计的人机交互反馈系统。

本项目基于 Fábio Ferreira 的原始设计进行了二次开发和优化，同时参考了 [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector) 项目的现代化实现，通过提供图形化界面，让用户能够在 AI 开发过程中实时提供文字反馈、上传图片、执行命令并查看输出，从而实现真正的人机协作开发模式。

## ✨ 核心功能

### 🎯 交互式反馈
- **📝 文字反馈**: 提供详细的文本反馈给 AI 助手
- **🖼️ 图片支持**: 支持多图片上传或剪贴板粘贴
- **💬 实时交互**: 与 AI 助手进行实时对话和反馈

### 🎨 用户界面
- **🌙 深色主题**: 护眼的深色界面，适合长时间使用
- **☀️ 浅色主题**: 清爽的浅色界面，适合明亮环境
- **🎛️ 主题切换**: 支持动态切换界面主题
- **📱 响应式设计**: 自适应窗口大小和布局

### ⚙️ 命令执行
- **🔄 实时输出**: 实时显示命令执行结果
- **📊 进程监控**: 监控命令执行状态和进程信息
- **🚀 自动执行**: 可选的启动时自动执行命令
- **💾 命令历史**: 保存和管理常用命令

### 🗂️ 项目管理
- **📁 项目特定设置**: 每个项目独立保存配置
- **⚙️ 配置持久化**: 使用 Qt QSettings 保存用户偏好
- **🔧 灵活配置**: 支持多种启动和配置方式

## 🏗️ 技术架构

### 核心技术栈
- **Python 3.11+**: 主要开发语言
- **FastMCP**: MCP 服务器框架
- **PySide6**: 跨平台 GUI 框架
- **psutil**: 系统进程管理
- **Pillow**: 图像处理库

### 项目结构
```
interactive-feedback-mcp/
├── server.py              # MCP 服务器主程序
├── feedback_ui.py          # GUI 界面实现
├── diagnose_mcp.py         # MCP 连接诊断工具
├── test_mcp.py            # MCP 服务器测试脚本
├── mcp_server.sh          # 服务器启动脚本
├── requirements.txt       # Python 依赖包
├── pyproject.toml         # 项目配置文件
├── cursor_mcp_config.json # Cursor 配置示例
├── images/                # 图片资源目录
├── logs/                  # 日志文件目录
└── README.md              # 项目说明文档
```

### 核心组件

#### 1. MCP 服务器 (`server.py`)
- 实现 MCP 协议的服务器端
- 提供 `interactive_feedback` 和 `get_image_info` 工具
- 处理与 AI 助手的通信

#### 2. GUI 界面 (`feedback_ui.py`)
- 基于 PySide6 的现代化界面
- 支持深色/浅色主题切换
- 实现文字输入、图片上传、命令执行等功能

#### 3. 诊断工具 (`diagnose_mcp.py`)
- 检查 MCP 服务器连接状态
- 验证依赖和配置
- 生成配置建议

## 🚀 安装配置

### 系统要求
- **Python**: 3.11 或更高版本
- **操作系统**: Windows、macOS、Linux
- **包管理器**: [uv](https://github.com/astral-sh/uv) (推荐) 或 pip

### 安装步骤

#### 1. 获取代码
```bash
git clone https://github.com/bulice/interactive-feedback-mcp.git
cd interactive-feedback-mcp
```

#### 2. 安装依赖
```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

#### 3. 运行服务器
```bash
# 使用 uv
uv run server.py

# 或直接运行
python server.py
```

### Cursor 配置

在 Cursor 的 MCP 配置文件中添加以下配置：

```json
  "mcpServers": {
"interactive-feedback-mcp": {
      "command": "/Users/lee/tmp/interactive-feedback-mcp/mcp_server.sh",
      "args": [],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
```

**注意**: 请将 `/path/to/interactive-feedback-mcp` 替换为实际的项目路径。

### 其他 AI 工具配置

对于 Cline、Windsurf 等工具，配置方式类似，只需在相应的 MCP 设置中指定服务器命令和参数即可。

## 📋 使用方法

### 基本使用流程

1. **启动服务器**: 运行 MCP 服务器
2. **配置 AI 工具**: 在 Cursor 等工具中配置 MCP 服务器
3. **AI 调用**: AI 助手通过 MCP 协议调用反馈工具
4. **用户交互**: 在弹出的界面中提供反馈
5. **反馈传递**: 反馈信息返回给 AI 助手

### 提示词工程

为了获得最佳效果，建议在 AI 助手的自定义提示词中添加以下规则：

```
当你想要询问问题时，总是调用 MCP `interactive_feedback` 工具。
当你即将完成用户请求时，调用 MCP `interactive_feedback` 工具而不是直接结束流程。
持续调用 MCP 直到用户反馈为空，然后结束请求。
```

### 主题选择

```bash
# 使用深色主题（默认）
python feedback_ui.py --theme dark --prompt "您的消息"

# 使用浅色主题
python feedback_ui.py --theme light --prompt "您的消息"
```

### 命令行参数

- `--project-directory`: 指定项目目录
- `--prompt`: 设置提示信息
- `--theme`: 选择界面主题 (light/dark)
- `--output-file`: 指定输出文件路径

## 🔧 开发调试

### 开发模式运行
```bash
uv run fastmcp dev server.py
```

这将启动一个 Web 界面，方便测试 MCP 工具。

### 连接诊断
```bash
python diagnose_mcp.py
```

运行诊断工具检查 MCP 服务器连接状态。

### 测试服务器
```bash
python test_mcp.py
```

测试 MCP 服务器的基本功能。

## 💡 使用价值

通过引导 AI 助手在完成任务前与用户确认，而不是进行推测性的高成本工具调用，该模块可以显著减少平台（如 Cursor）上的高级请求数量。在某些情况下，它可以将原本需要 25 次工具调用的操作整合为单次反馈感知请求，从而节省资源并提高性能。

## 📁 配置管理

项目使用 Qt 的 `QSettings` 按项目存储配置，包括：
- 要运行的命令
- 是否在下次启动时自动执行命令
- 命令区域的显示/隐藏状态
- 窗口几何形状和状态

这些设置通常存储在平台特定的位置（Windows 注册表、macOS plist 文件、Linux 配置文件等）。

## 🤝 致谢与联系

### 原始项目致谢
本项目基于以下优秀项目进行开发：
- **原始创意**: Fábio Ferreira 的 [Interactive Feedback MCP](https://x.com/fabiomlferreira)
- **现代化实现**: [sanshao85/mcp-feedback-collector](https://github.com/sanshao85/mcp-feedback-collector)

感谢这些开发者的原创贡献和开源精神。如果您觉得这个项目有用，建议关注原作者们的工作。

### 当前维护
- **维护者**: bulice
- **项目地址**: https://github.com/bulice/interactive-feedback-mcp
- **问题反馈**: 请在 GitHub 项目页面提交 Issue

### 相关资源
请查看 [dotcursorrules.com](https://dotcursorrules.com/) 获取更多 AI 辅助开发工作流程的增强资源。

## 📄 许可证

本项目采用开源许可证，详见 [LICENSE](LICENSE) 文件。
