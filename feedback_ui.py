# Interactive Feedback MCP UI
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
import os
import sys
import json
import psutil
import argparse
import subprocess
import threading
import hashlib
from typing import Optional, TypedDict

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QGroupBox,
    QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QFont, QFontDatabase, QPalette, QColor, QPixmap

class FeedbackResult(TypedDict):
    command_logs: str
    interactive_feedback: str

class FeedbackConfig(TypedDict):
    run_command: str
    execute_automatically: bool

def set_dark_title_bar(widget: QWidget, dark_title_bar: bool) -> None:
    # Ensure we're on Windows
    if sys.platform != "win32":
        return

    from ctypes import windll, c_uint32, byref

    # Get Windows build number
    build_number = sys.getwindowsversion().build
    if build_number < 17763:  # Windows 10 1809 minimum
        return

    # Check if the widget's property already matches the setting
    dark_prop = widget.property("DarkTitleBar")
    if dark_prop is not None and dark_prop == dark_title_bar:
        return

    # Set the property (True if dark_title_bar != 0, False otherwise)
    widget.setProperty("DarkTitleBar", dark_title_bar)

    # Load dwmapi.dll and call DwmSetWindowAttribute
    dwmapi = windll.dwmapi
    hwnd = widget.winId()  # Get the window handle
    attribute = 20 if build_number >= 18985 else 19  # Use newer attribute for newer builds
    c_dark_title_bar = c_uint32(dark_title_bar)  # Convert to C-compatible uint32
    dwmapi.DwmSetWindowAttribute(hwnd, attribute, byref(c_dark_title_bar), 4)

    # HACK: Create a 1x1 pixel frameless window to force redraw
    temp_widget = QWidget(None, Qt.FramelessWindowHint)
    temp_widget.resize(1, 1)
    temp_widget.move(widget.pos())
    temp_widget.show()
    temp_widget.deleteLater()  # Safe deletion in Qt event loop

def get_dark_mode_palette(app: QApplication):
    darkPalette = app.palette()
    
    # 主背景色 - 使用更深的灰色
    darkPalette.setColor(QPalette.Window, QColor(35, 35, 38))
    # 主文本色 - 使用更柔和的白色
    darkPalette.setColor(QPalette.WindowText, QColor(240, 240, 240))
    # 禁用状态的文本
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
    
    # 输入框背景 - 稍微亮一些便于区分
    darkPalette.setColor(QPalette.Base, QColor(45, 45, 48))
    # 交替背景色
    darkPalette.setColor(QPalette.AlternateBase, QColor(55, 55, 58))
    
    # 工具提示
    darkPalette.setColor(QPalette.ToolTipBase, QColor(50, 50, 53))
    darkPalette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
    
    # 输入框文本
    darkPalette.setColor(QPalette.Text, QColor(235, 235, 235))
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(110, 110, 110))
    
    # 边框和阴影
    darkPalette.setColor(QPalette.Dark, QColor(25, 25, 28))
    darkPalette.setColor(QPalette.Shadow, QColor(15, 15, 18))
    
    # 按钮
    darkPalette.setColor(QPalette.Button, QColor(60, 60, 63))
    darkPalette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(100, 100, 100))
    
    # 亮文本（错误等）
    darkPalette.setColor(QPalette.BrightText, QColor(255, 100, 100))
    
    # 链接和高亮
    darkPalette.setColor(QPalette.Link, QColor(100, 150, 255))
    darkPalette.setColor(QPalette.Highlight, QColor(80, 140, 250))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(60, 60, 65))
    darkPalette.setColor(QPalette.HighlightedText, QColor(250, 250, 250))
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(120, 120, 120))
    
    # 占位符文本
    darkPalette.setColor(QPalette.PlaceholderText, QColor(140, 140, 140))
    
    return darkPalette

def get_light_mode_palette(app: QApplication):
    lightPalette = app.palette()
    
    # 主背景色 - 使用温和的浅色
    lightPalette.setColor(QPalette.Window, QColor(248, 249, 250))
    # 主文本色 - 使用深灰色而非纯黑
    lightPalette.setColor(QPalette.WindowText, QColor(33, 37, 41))
    # 禁用状态的文本
    lightPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(108, 117, 125))
    
    # 输入框背景 - 纯白色
    lightPalette.setColor(QPalette.Base, QColor(255, 255, 255))
    # 交替背景色
    lightPalette.setColor(QPalette.AlternateBase, QColor(241, 243, 245))
    
    # 工具提示
    lightPalette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    lightPalette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    
    # 输入框文本
    lightPalette.setColor(QPalette.Text, QColor(33, 37, 41))
    lightPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(134, 142, 150))
    
    # 边框和阴影
    lightPalette.setColor(QPalette.Dark, QColor(173, 181, 189))
    lightPalette.setColor(QPalette.Shadow, QColor(134, 142, 150))
    
    # 按钮
    lightPalette.setColor(QPalette.Button, QColor(233, 236, 239))
    lightPalette.setColor(QPalette.ButtonText, QColor(33, 37, 41))
    lightPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(134, 142, 150))
    
    # 亮文本（错误等）
    lightPalette.setColor(QPalette.BrightText, QColor(220, 53, 69))
    
    # 链接和高亮
    lightPalette.setColor(QPalette.Link, QColor(13, 110, 253))
    lightPalette.setColor(QPalette.Highlight, QColor(13, 110, 253))
    lightPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(173, 181, 189))
    lightPalette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    lightPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(134, 142, 150))
    
    # 占位符文本
    lightPalette.setColor(QPalette.PlaceholderText, QColor(108, 117, 125))
    
    return lightPalette

def kill_tree(process: subprocess.Popen):
    killed: list[psutil.Process] = []
    parent = psutil.Process(process.pid)
    for proc in parent.children(recursive=True):
        try:
            proc.kill()
            killed.append(proc)
        except psutil.Error:
            pass
    try:
        parent.kill()
    except psutil.Error:
        pass
    killed.append(parent)

    # Terminate any remaining processes
    for proc in killed:
        try:
            if proc.is_running():
                proc.terminate()
        except psutil.Error:
            pass

def get_user_environment() -> dict[str, str]:
    if sys.platform != "win32":
        return os.environ.copy()

    import ctypes
    from ctypes import wintypes

    # Load required DLLs
    advapi32 = ctypes.WinDLL("advapi32")
    userenv = ctypes.WinDLL("userenv")
    kernel32 = ctypes.WinDLL("kernel32")

    # Constants
    TOKEN_QUERY = 0x0008

    # Function prototypes
    OpenProcessToken = advapi32.OpenProcessToken
    OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    OpenProcessToken.restype = wintypes.BOOL

    CreateEnvironmentBlock = userenv.CreateEnvironmentBlock
    CreateEnvironmentBlock.argtypes = [ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.BOOL]
    CreateEnvironmentBlock.restype = wintypes.BOOL

    DestroyEnvironmentBlock = userenv.DestroyEnvironmentBlock
    DestroyEnvironmentBlock.argtypes = [wintypes.LPVOID]
    DestroyEnvironmentBlock.restype = wintypes.BOOL

    GetCurrentProcess = kernel32.GetCurrentProcess
    GetCurrentProcess.argtypes = []
    GetCurrentProcess.restype = wintypes.HANDLE

    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [wintypes.HANDLE]
    CloseHandle.restype = wintypes.BOOL

    # Get process token
    token = wintypes.HANDLE()
    if not OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)):
        raise RuntimeError("Failed to open process token")

    try:
        # Create environment block
        environment = ctypes.c_void_p()
        if not CreateEnvironmentBlock(ctypes.byref(environment), token, False):
            raise RuntimeError("Failed to create environment block")

        try:
            # Convert environment block to list of strings
            result = {}
            env_ptr = ctypes.cast(environment, ctypes.POINTER(ctypes.c_wchar))
            offset = 0

            while True:
                # Get string at current offset
                current_string = ""
                while env_ptr[offset] != "\0":
                    current_string += env_ptr[offset]
                    offset += 1

                # Skip null terminator
                offset += 1

                # Break if we hit double null terminator
                if not current_string:
                    break

                equal_index = current_string.index("=")
                if equal_index == -1:
                    continue

                key = current_string[:equal_index]
                value = current_string[equal_index + 1:]
                result[key] = value

            return result

        finally:
            DestroyEnvironmentBlock(environment)

    finally:
        CloseHandle(token)

class FeedbackTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # Find the parent FeedbackUI instance and call submit
            parent = self.parent()
            while parent and not isinstance(parent, FeedbackUI):
                parent = parent.parent()
            if parent:
                parent._submit_feedback()
        else:
            super().keyPressEvent(event)

class LogSignals(QObject):
    append_log = Signal(str)

class FeedbackUI(QMainWindow):
    def __init__(self, project_directory: str, prompt: str, dark_theme: bool = True):
        super().__init__()
        self.project_directory = project_directory
        self.prompt = prompt
        self.dark_theme = dark_theme  # 存储主题选择

        self.process: Optional[subprocess.Popen] = None
        self.log_buffer = []
        self.feedback_result = None
        self.log_signals = LogSignals()
        self.log_signals.append_log.connect(self._append_log)
        
        # 图片相关属性
        self.selected_images = []  # 存储选择的图片路径
        self.image_widgets = []  # 存储图片显示组件

        self.setWindowTitle("Interactive Feedback MCP")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        
        # Load general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(800, 600)
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 800) // 2
            y = (screen.height() - 600) // 2
            self.move(x, y)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        self.settings.endGroup() # End "MainWindow_General" group
        
        # Load project-specific settings (command, auto-execute, command section visibility)
        self.project_group_name = get_project_settings_group(self.project_directory)
        self.settings.beginGroup(self.project_group_name)
        loaded_run_command = self.settings.value("run_command", "", type=str)
        loaded_execute_auto = self.settings.value("execute_automatically", False, type=bool)
        command_section_visible = self.settings.value("commandSectionVisible", False, type=bool)
        self.settings.endGroup() # End project-specific group
        
        self.config: FeedbackConfig = {
            "run_command": loaded_run_command,
            "execute_automatically": loaded_execute_auto
        }

        self._create_ui() # self.config is used here to set initial values

        # Set command section visibility AFTER _create_ui has created relevant widgets
        self.command_group.setVisible(command_section_visible)
        if command_section_visible:
            self.toggle_command_button.setText("🔼 隐藏命令区域")
        else:
            self.toggle_command_button.setText("📁 AI工作完成汇报")

        set_dark_title_bar(self, True)

        if self.config.get("execute_automatically", False):
            self._run_command()

    def _format_windows_path(self, path: str) -> str:
        if sys.platform == "win32":
            # Convert forward slashes to backslashes
            path = path.replace("/", "\\")
            # Capitalize drive letter if path starts with x:\
            if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
                path = path[0].upper() + path[1:]
        return path

    def _get_theme_stylesheet(self) -> str:
        """根据当前主题返回相应的样式表"""
        if self.dark_theme:
            return self._get_dark_theme_stylesheet()
        else:
            return self._get_light_theme_stylesheet()

    def _get_dark_theme_stylesheet(self) -> str:
        """暗黑主题样式表"""
        return """
            QMainWindow {
                background-color: #232326;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #404043;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 5px;
                background-color: #2d2d30;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #e0e0e0;
                background-color: #2d2d30;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                color: #ffffff;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
            QPushButton:disabled {
                background-color: #404043;
                color: #808080;
            }
            QLineEdit {
                border: 2px solid #404043;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: #3c3c3f;
                color: #e8e8e8;
                selection-background-color: #5090d0;
            }
            QLineEdit:focus {
                border-color: #0e639c;
            }
            QTextEdit {
                border: 2px solid #404043;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: #3c3c3f;
                color: #e8e8e8;
                selection-background-color: #5090d0;
            }
            QTextEdit:focus {
                border-color: #0e639c;
            }
            QCheckBox {
                font-size: 12px;
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #404043;
                border-radius: 3px;
                background-color: #3c3c3f;
            }
            QCheckBox::indicator:checked {
                background-color: #0e639c;
                border-color: #0e639c;
            }
            QCheckBox::indicator:checked::before {
                content: "✓";
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QScrollArea {
                border: 2px dashed #606063;
                border-radius: 8px;
                background-color: #3c3c3f;
            }
        """

    def _get_light_theme_stylesheet(self) -> str:
        """明亮主题样式表"""
        return """
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 5px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #212529;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0d6efd;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                color: #ffffff;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: #ffffff;
                color: #212529;
                selection-background-color: #0d6efd;
            }
            QLineEdit:focus {
                border-color: #0d6efd;
            }
            QTextEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: #ffffff;
                color: #212529;
                selection-background-color: #0d6efd;
            }
            QTextEdit:focus {
                border-color: #0d6efd;
            }
            QCheckBox {
                font-size: 12px;
                color: #212529;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #ced4da;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
            QCheckBox::indicator:checked::before {
                content: "✓";
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QLabel {
                color: #212529;
                font-size: 12px;
            }
            QScrollArea {
                border: 2px dashed #adb5bd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """

    def _get_themed_button_style(self, button_type: str) -> str:
        """根据主题和按钮类型返回特定样式"""
        if self.dark_theme:
            styles = {
                'toggle': """
                    QPushButton {
                        background-color: #404043;
                        color: #e0e0e0;
                        text-align: left;
                        padding: 12px 16px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #4a4a4d;
                    }
                """,
                'save': """
                    QPushButton {
                        background-color: #2d7d32;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #388e3c;
                    }
                """,
                'danger': """
                    QPushButton {
                        background-color: #d32f2f;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #f44336;
                    }
                """,
                'console': """
                    QTextEdit {
                        background-color: #1e1e1e;
                        color: #d4d4d4;
                        border: 1px solid #404043;
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    }
                """,
                'submit': """
                    QPushButton {
                        background-color: #2e7d32;
                        font-size: 13px;
                        min-height: 25px;
                    }
                    QPushButton:hover {
                        background-color: #388e3c;
                    }
                """,
                'image_select': """
                    QPushButton {
                        background-color: #455a64;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #546e7a;
                    }
                """,
                'image_paste': """
                    QPushButton {
                        background-color: #6a4c93;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #7b5aa6;
                    }
                """,
                'description': """
                    background-color: #3c3c3f;
                    border: 1px solid #555558;
                    border-radius: 6px;
                    padding: 12px;
                    color: #e0e0e0;
                    font-size: 12px;
                    line-height: 1.4;
                """,
                'hint': """
                    font-size: 11px; 
                    color: #b0b0b0; 
                    font-style: italic;
                    margin: 10px 0px;
                    padding: 8px;
                    background-color: #3c3c3f;
                    border-radius: 4px;
                """,
                'working_dir': """
                    color: #b0b0b0; 
                    font-size: 11px; 
                    font-style: italic;
                    margin: 5px 0px;
                """
            }
        else:
            styles = {
                'toggle': """
                    QPushButton {
                        background-color: #e9ecef;
                        color: #212529;
                        text-align: left;
                        padding: 12px 16px;
                        font-size: 13px;
                        border: 1px solid #ced4da;
                    }
                    QPushButton:hover {
                        background-color: #f8f9fa;
                        border-color: #adb5bd;
                    }
                """,
                'save': """
                    QPushButton {
                        background-color: #198754;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #157347;
                    }
                """,
                'danger': """
                    QPushButton {
                        background-color: #dc3545;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #bb2d3b;
                    }
                """,
                'console': """
                    QTextEdit {
                        background-color: #f8f9fa;
                        color: #212529;
                        border: 1px solid #ced4da;
                        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    }
                """,
                'submit': """
                    QPushButton {
                        background-color: #198754;
                        font-size: 13px;
                        min-height: 25px;
                    }
                    QPushButton:hover {
                        background-color: #157347;
                    }
                """,
                'image_select': """
                    QPushButton {
                        background-color: #6c757d;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #5c636a;
                    }
                """,
                'image_paste': """
                    QPushButton {
                        background-color: #6f42c1;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #5a2d91;
                    }
                """,
                'description': """
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 12px;
                    color: #212529;
                    font-size: 12px;
                    line-height: 1.4;
                """,
                'hint': """
                    font-size: 11px; 
                    color: #6c757d; 
                    font-style: italic;
                    margin: 10px 0px;
                    padding: 8px;
                    background-color: #e9ecef;
                    border-radius: 4px;
                """,
                'working_dir': """
                    color: #6c757d; 
                    font-size: 11px; 
                    font-style: italic;
                    margin: 5px 0px;
                """
            }
        
        return styles.get(button_type, "")

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)  # 增加间距
        layout.setContentsMargins(20, 20, 20, 20)  # 增加边距

        # 应用自定义样式
        self.setStyleSheet(self._get_theme_stylesheet())

        # 标题区域
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加图标和标题
        title_icon = QLabel("🎯")
        title_icon.setStyleSheet("font-size: 24px;")
        title_text = QLabel("工作完成汇报与反馈收集")
        
        # 根据主题设置标题文字颜色
        if self.dark_theme:
            title_style = """
                font-size: 18px; 
                font-weight: bold; 
                color: #e8e8e8; 
                margin: 0px;
                padding: 5px 0px;
            """
        else:
            title_style = """
                font-size: 18px; 
                font-weight: bold; 
                color: #212529; 
                margin: 0px;
                padding: 5px 0px;
            """
        title_text.setStyleSheet(title_style)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        layout.addWidget(title_widget)

        # Toggle Command Section Button
        self.toggle_command_button = QPushButton("📁 AI工作完成汇报")
        self.toggle_command_button.setStyleSheet(self._get_themed_button_style('toggle'))
        self.toggle_command_button.clicked.connect(self._toggle_command_section)
        layout.addWidget(self.toggle_command_button)

        # Command section
        self.command_group = QGroupBox("命令执行")
        command_layout = QVBoxLayout(self.command_group)
        command_layout.setSpacing(10)

        # Working directory label
        formatted_path = self._format_windows_path(self.project_directory)
        working_dir_label = QLabel(f"工作目录: {formatted_path}")
        working_dir_label.setStyleSheet(self._get_themed_button_style('working_dir'))
        command_layout.addWidget(working_dir_label)

        # Command input row
        command_input_layout = QHBoxLayout()
        command_input_layout.setSpacing(10)
        self.command_entry = QLineEdit()
        self.command_entry.setText(self.config["run_command"])
        self.command_entry.setPlaceholderText("输入要执行的命令...")
        self.command_entry.returnPressed.connect(self._run_command)
        self.command_entry.textChanged.connect(self._update_config)
        self.run_button = QPushButton("▶ 运行")
        self.run_button.setMinimumWidth(80)
        self.run_button.clicked.connect(self._run_command)

        command_input_layout.addWidget(self.command_entry)
        command_input_layout.addWidget(self.run_button)
        command_layout.addLayout(command_input_layout)

        # Auto-execute and save config row
        auto_layout = QHBoxLayout()
        self.auto_check = QCheckBox("下次启动时自动执行")
        self.auto_check.setChecked(self.config.get("execute_automatically", False))
        self.auto_check.stateChanged.connect(self._update_config)

        save_button = QPushButton("💾 保存配置")
        save_button.setStyleSheet(self._get_themed_button_style('save'))
        save_button.clicked.connect(self._save_config)

        auto_layout.addWidget(self.auto_check)
        auto_layout.addStretch()
        auto_layout.addWidget(save_button)
        command_layout.addLayout(auto_layout)

        # Console section (now part of command_group)
        console_group = QGroupBox("控制台输出")
        console_layout_internal = QVBoxLayout(console_group)
        console_group.setMinimumHeight(200)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        font = QFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        font.setPointSize(10)
        self.log_text.setFont(font)
        self.log_text.setStyleSheet(self._get_themed_button_style('console'))
        console_layout_internal.addWidget(self.log_text)

        # Clear button
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("🗑 清空日志")
        self.clear_button.setStyleSheet(self._get_themed_button_style('danger'))
        self.clear_button.clicked.connect(self.clear_logs)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        console_layout_internal.addLayout(button_layout)
        
        command_layout.addWidget(console_group)

        self.command_group.setVisible(False) 
        layout.addWidget(self.command_group)

        # Feedback section with adjusted height
        self.feedback_group = QGroupBox("💬 您的文字反馈（可选）")
        feedback_layout = QVBoxLayout(self.feedback_group)
        feedback_layout.setSpacing(12)

        # Short description label (from self.prompt)
        self.description_label = QLabel(self.prompt)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(self._get_themed_button_style('description'))
        feedback_layout.addWidget(self.description_label)

        self.feedback_text = FeedbackTextEdit()
        font_metrics = self.feedback_text.fontMetrics()
        row_height = font_metrics.height()
        # Calculate height for 5 lines + some padding for margins
        padding = self.feedback_text.contentsMargins().top() + self.feedback_text.contentsMargins().bottom() + 5
        self.feedback_text.setMinimumHeight(5 * row_height + padding)

        self.feedback_text.setPlaceholderText("请在此输入您的反馈、建议或问题...")
        submit_button = QPushButton("✅ 提交反馈 (Ctrl+Enter)")
        submit_button.setStyleSheet(self._get_themed_button_style('submit'))
        submit_button.clicked.connect(self._submit_feedback)

        feedback_layout.addWidget(self.feedback_text)
        feedback_layout.addWidget(submit_button)

        # 图片反馈区域（可选，支持多张）
        image_group = QGroupBox("🖼 图片反馈（可选，支持多张）")
        image_layout = QVBoxLayout(image_group)
        
        # 图片选择按钮
        image_button_layout = QHBoxLayout()
        select_images_button = QPushButton("📁 选择图片")
        select_images_button.setStyleSheet(self._get_themed_button_style('image_select'))
        select_images_button.clicked.connect(self._select_images)
        
        paste_image_button = QPushButton("📋 粘贴图片")
        paste_image_button.setStyleSheet(self._get_themed_button_style('image_paste'))
        paste_image_button.clicked.connect(self._paste_image)
        
        clear_images_button = QPushButton("🗑 清空图片")
        clear_images_button.setStyleSheet(self._get_themed_button_style('danger'))
        clear_images_button.clicked.connect(self._clear_images)
        
        image_button_layout.addWidget(select_images_button)
        image_button_layout.addWidget(paste_image_button)
        image_button_layout.addWidget(clear_images_button)
        image_button_layout.addStretch()
        image_layout.addLayout(image_button_layout)
        
        # 图片显示区域
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidgetResizable(True)
        self.image_scroll_area.setMinimumHeight(150)
        
        self.image_container = QWidget()
        self.image_container_layout = QHBoxLayout(self.image_container)
        self.image_container_layout.setAlignment(Qt.AlignLeft)
        
        # 默认提示标签
        self.no_image_label = QLabel("📷 尚未选择图片\n点击上方按钮添加图片")
        self.no_image_label.setAlignment(Qt.AlignCenter)
        
        # 根据主题设置无图片标签样式
        if self.dark_theme:
            no_image_style = """
                color: #a0a0a0;
                font-size: 14px;
                padding: 40px;
            """
        else:
            no_image_style = """
                color: #6c757d;
                font-size: 14px;
                padding: 40px;
            """
        self.no_image_label.setStyleSheet(no_image_style)
        self.image_container_layout.addWidget(self.no_image_label)
        
        self.image_scroll_area.setWidget(self.image_container)
        image_layout.addWidget(self.image_scroll_area)
        
        feedback_layout.addWidget(image_group)

        # 操作按钮区域
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        confirm_button = QPushButton("✅ 确认")
        confirm_button.setStyleSheet(self._get_themed_button_style('save'))
        
        cancel_button = QPushButton("❌ 取消")
        cancel_button.setStyleSheet(self._get_themed_button_style('danger'))
        
        action_layout.addStretch()
        action_layout.addWidget(confirm_button)
        action_layout.addWidget(cancel_button)
        feedback_layout.addLayout(action_layout)

        # Set minimum height for feedback_group to accommodate its contents
        self.feedback_group.setMinimumHeight(500)

        # Add widgets in a specific order
        layout.addWidget(self.feedback_group)

        # 提示标签
        hint_label = QLabel("💡 提示：您可以只提供文字反馈、只提供图片，或者两者都提供（支持多张图片）")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet(self._get_themed_button_style('hint'))
        layout.addWidget(hint_label)

        # Credits/Contact Label - 更加美观
        contact_label = QLabel('需要改进？联系 Fábio Ferreira 在 <a href="https://x.com/fabiomlferreira" style="color: #5090d0;">X.com</a> 或访问 <a href="https://dotcursorrules.com/" style="color: #5090d0;">dotcursorrules.com</a>')
        contact_label.setOpenExternalLinks(True)
        contact_label.setAlignment(Qt.AlignCenter)
        
        # 根据主题设置联系标签样式
        if self.dark_theme:
            contact_style = """
                font-size: 10px; 
                color: #909090;
                padding: 8px;
                margin: 5px 0px;
            """
        else:
            contact_style = """
                font-size: 10px; 
                color: #6c757d;
                padding: 8px;
                margin: 5px 0px;
            """
        contact_label.setStyleSheet(contact_style)
        layout.addWidget(contact_label)

    def _toggle_command_section(self):
        is_visible = self.command_group.isVisible()
        self.command_group.setVisible(not is_visible)
        if not is_visible:
            self.toggle_command_button.setText("🔼 隐藏命令区域")
        else:
            self.toggle_command_button.setText("📁 AI工作完成汇报")
        
        # Immediately save the visibility state for this project
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("commandSectionVisible", self.command_group.isVisible())
        self.settings.endGroup()

        # Adjust window height only
        new_height = self.centralWidget().sizeHint().height()
        if self.command_group.isVisible() and self.command_group.layout().sizeHint().height() > 0:
             # if command group became visible and has content, ensure enough height
             min_content_height = self.command_group.layout().sizeHint().height() + self.feedback_group.minimumHeight() + self.toggle_command_button.height() + self.centralWidget().layout().spacing() * 2
             new_height = max(new_height, min_content_height)

        current_width = self.width()
        self.resize(current_width, new_height)

    def _update_config(self):
        self.config["run_command"] = self.command_entry.text()
        self.config["execute_automatically"] = self.auto_check.isChecked()

    def _append_log(self, text: str):
        self.log_buffer.append(text)
        self.log_text.append(text.rstrip())
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def _check_process_status(self):
        if self.process and self.process.poll() is not None:
            # Process has terminated
            exit_code = self.process.poll()
            self._append_log(f"\n进程已退出，代码: {exit_code}\n")
            self.run_button.setText("▶ 运行")
            self.process = None
            self.activateWindow()
            self.feedback_text.setFocus()

    def _run_command(self):
        if self.process:
            kill_tree(self.process)
            self.process = None
            self.run_button.setText("▶ 运行")
            return

        # Clear the log buffer but keep UI logs visible
        self.log_buffer = []

        command = self.command_entry.text()
        if not command:
            self._append_log("请输入要执行的命令\n")
            return

        self._append_log(f"$ {command}\n")
        self.run_button.setText("⏹ 停止")

        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=get_user_environment(),
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="ignore",
                close_fds=True,
            )

            def read_output(pipe):
                for line in iter(pipe.readline, ""):
                    self.log_signals.append_log.emit(line)

            threading.Thread(
                target=read_output,
                args=(self.process.stdout,),
                daemon=True
            ).start()

            threading.Thread(
                target=read_output,
                args=(self.process.stderr,),
                daemon=True
            ).start()

            # Start process status checking
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self._check_process_status)
            self.status_timer.start(100)  # Check every 100ms

        except Exception as e:
            self._append_log(f"运行命令时出错: {str(e)}\n")
            self.run_button.setText("▶ 运行")

    def _submit_feedback(self):
        # 收集反馈信息，包括文字和图片
        feedback_data = {
            'text_feedback': self.feedback_text.toPlainText().strip(),
            'images': self.selected_images.copy()
        }
        
        self.feedback_result = FeedbackResult(
            command_logs="".join(self.log_buffer),
            interactive_feedback=json.dumps(feedback_data, ensure_ascii=False, indent=2)
        )
        self.close()

    def clear_logs(self):
        self.log_buffer = []
        self.log_text.clear()

    def _save_config(self):
        # Save run_command and execute_automatically to QSettings under project group
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("run_command", self.config["run_command"])
        self.settings.setValue("execute_automatically", self.config["execute_automatically"])
        self.settings.endGroup()
        self._append_log("已保存此项目的配置。\n")

    def _select_images(self):
        """选择图片文件"""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.tiff);;所有文件 (*)"
        )
        
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.selected_images:
                    self.selected_images.append(file_path)
            self._update_image_display()

    def _paste_image(self):
        """从剪贴板粘贴图片"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        
        if not pixmap.isNull():
            # 保存临时图片文件
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            if pixmap.save(temp_path, 'PNG'):
                if temp_path not in self.selected_images:
                    self.selected_images.append(temp_path)
                self._update_image_display()
            else:
                self._append_log("保存剪贴板图片失败。\n")
        else:
            self._append_log("剪贴板中没有图片。\n")

    def _clear_images(self):
        """清空所有选择的图片"""
        # 清理临时文件
        import tempfile
        for image_path in self.selected_images:
            if tempfile.gettempdir() in image_path:
                try:
                    os.remove(image_path)
                except:
                    pass
        
        self.selected_images.clear()
        self._update_image_display()

    def _update_image_display(self):
        """更新图片显示区域"""
        # 清空当前显示的图片组件
        for widget in self.image_widgets:
            widget.deleteLater()
        self.image_widgets.clear()
        
        if not self.selected_images:
            # 没有图片时显示提示
            self.no_image_label.setVisible(True)
        else:
            # 隐藏提示标签
            self.no_image_label.setVisible(False)
            
            # 为每个图片创建显示组件
            for i, image_path in enumerate(self.selected_images):
                image_widget = self._create_image_widget(image_path, i)
                self.image_container_layout.addWidget(image_widget)
                self.image_widgets.append(image_widget)

    def _create_image_widget(self, image_path: str, index: int) -> QWidget:
        """创建单个图片显示组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 图片标签
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            # 缩放图片到合适大小
            scaled_pixmap = pixmap.scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("❌\n加载失败")
            image_label.setAlignment(Qt.AlignCenter)
        
        # 根据主题设置图片标签样式
        if self.dark_theme:
            image_label_style = """
                QLabel {
                    border: 1px solid #606063;
                    border-radius: 4px;
                    background-color: #4a4a4d;
                    padding: 5px;
                }
            """
            name_label_style = """
                color: #c0c0c0;
                font-size: 10px;
                margin: 2px 0px;
            """
        else:
            image_label_style = """
                QLabel {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    padding: 5px;
                }
            """
            name_label_style = """
                color: #495057;
                font-size: 10px;
                margin: 2px 0px;
            """
        
        image_label.setStyleSheet(image_label_style)
        image_label.setMinimumSize(130, 100)
        image_label.setAlignment(Qt.AlignCenter)
        
        # 文件名标签
        file_name = os.path.basename(image_path)
        if len(file_name) > 15:
            file_name = file_name[:12] + "..."
        name_label = QLabel(file_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(name_label_style)
        
        # 删除按钮
        remove_button = QPushButton("❌")
        remove_button.setFixedSize(20, 20)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: none;
                border-radius: 10px;
                font-size: 10px;
                color: white;
            }
            QPushButton:hover {
                background-color: #bb2d3b;
            }
        """)
        remove_button.clicked.connect(lambda: self._remove_image(index))
        
        # 布局
        layout.addWidget(image_label)
        layout.addWidget(name_label)
        layout.addWidget(remove_button, alignment=Qt.AlignCenter)
        
        widget.setMaximumWidth(140)
        return widget

    def _remove_image(self, index: int):
        """删除指定索引的图片"""
        if 0 <= index < len(self.selected_images):
            image_path = self.selected_images[index]
            
            # 如果是临时文件，删除它
            import tempfile
            if tempfile.gettempdir() in image_path:
                try:
                    os.remove(image_path)
                except:
                    pass
            
            self.selected_images.pop(index)
            self._update_image_display()

    def closeEvent(self, event):
        # Save general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()

        # Save project-specific command section visibility (this is now slightly redundant due to immediate save in toggle, but harmless)
        self.settings.beginGroup(self.project_group_name)
        self.settings.setValue("commandSectionVisible", self.command_group.isVisible())
        self.settings.endGroup()

        # 清理临时图片文件
        import tempfile
        for image_path in self.selected_images:
            if tempfile.gettempdir() in image_path:
                try:
                    os.remove(image_path)
                except:
                    pass

        if self.process:
            kill_tree(self.process)
        super().closeEvent(event)

    def run(self) -> FeedbackResult:
        self.show()
        QApplication.instance().exec()

        if self.process:
            kill_tree(self.process)

        if not self.feedback_result:
            return FeedbackResult(command_logs="".join(self.log_buffer), interactive_feedback="")

        return self.feedback_result

def get_project_settings_group(project_dir: str) -> str:
    # Create a safe, unique group name from the project directory path
    # Using only the last component + hash of full path to keep it somewhat readable but unique
    basename = os.path.basename(os.path.normpath(project_dir))
    full_hash = hashlib.md5(project_dir.encode('utf-8')).hexdigest()[:8]
    return f"{basename}_{full_hash}"

def feedback_ui(project_directory: str, prompt: str, output_file: Optional[str] = None, dark_theme: bool = True) -> Optional[FeedbackResult]:
    app = QApplication.instance() or QApplication()
    
    # 根据主题选择应用相应的调色板
    if dark_theme:
        app.setPalette(get_dark_mode_palette(app))
    else:
        app.setPalette(get_light_mode_palette(app))
    
    app.setStyle("Fusion")
    ui = FeedbackUI(project_directory, prompt, dark_theme)
    result = ui.run()

    if output_file and result:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # Save the result to the output file
        with open(output_file, "w") as f:
            json.dump(result, f)
        return None

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the feedback UI")
    parser.add_argument("--project-directory", default=os.getcwd(), help="The project directory to run the command in")
    parser.add_argument("--prompt", default="I implemented the changes you requested.", help="The prompt to show to the user")
    parser.add_argument("--output-file", help="Path to save the feedback result as JSON")
    parser.add_argument("--theme", choices=['dark', 'light'], default='dark', help="UI theme: dark or light (default: dark)")
    args = parser.parse_args()

    # 将主题参数转换为布尔值
    dark_theme = args.theme == 'dark'
    
    result = feedback_ui(args.project_directory, args.prompt, args.output_file, dark_theme)
    if result:
        print(f"\nLogs collected: \n{result['command_logs']}")
        print(f"\nFeedback received:\n{result['interactive_feedback']}")
    sys.exit(0)
