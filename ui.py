from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QFileDialog, QCheckBox, QTextEdit,
                           QDialog, QLineEdit, QFormLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor, QTextCharFormat, QBrush, QIcon
import os
import time

class DropArea(QLabel):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n将文件拖拽到此处\n或点击选择文件')
        self.setFixedHeight(180)  # 固定高度
        self.setBaseStyle()
        self.setAcceptDrops(True)

    def setBaseStyle(self):
        """设置基础样式"""
        self.setStyleSheet('''
            QLabel {
                border: 2px dashed #4a9eff;
                border-radius: 8px;
                background-color: #f8fafc;
                font-size: 14px;
                color: #666666;
                min-width: 400px;  /* 添加最小宽度 */
            }
        ''')

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet('''
                QLabel {
                    border: 2px dashed #3d8ee6;
                    border-radius: 8px;
                    background-color: #f0f7ff;
                    font-size: 14px;
                    color: #666666;
                    min-width: 400px;  /* 添加最小宽度 */
                }
            ''')

    def dragLeaveEvent(self, event):
        self.setBaseStyle()  # 恢复基础样式

    def dropEvent(self, event: QDropEvent):
        self.setBaseStyle()  # 恢复基础样式
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            paths.append(path)
        self.main_window.handle_dropped_files(paths)

class LogDisplay(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        
    def append_log(self, text, level="info"):
        """
        添加带颜色的日志
        level: info, success, error, warning
        """
        color_map = {
            "info": "#666666",      # 深灰色
            "success": "#2ecc71",   # 翠绿色
            "error": "#e74c3c",     # 红色
            "warning": "#f39c12",   # 橙色
        }
        
        # 添加时间戳
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # 添加等级图标
        level_icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        
        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(color_map.get(level, "#333333"))))
        
        self.moveCursor(self.textCursor().End)
        self.textCursor().insertText(
            f"[{timestamp}] {level_icons.get(level, '')} {text}\n", 
            format
        )
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)
        
        # 图标和标题
        title_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("icon.png").pixmap(16, 16))  # 需要添加图标文件
        title_label = QLabel("md2picgo")
        title_label.setStyleSheet("color: #333333; font-size: 13px;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        self.min_button = QPushButton("—")
        self.max_button = QPushButton("□")
        self.close_button = QPushButton("×")
        
        for btn in [self.min_button, self.max_button, self.close_button]:
            btn.setFixedSize(40, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #666666;
                    font-family: Arial;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
            """)
            
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #666666;
                font-family: Arial;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff4d4d;
                color: white;
            }
        """)
        
        btn_layout.addWidget(self.min_button)
        btn_layout.addWidget(self.max_button)
        btn_layout.addWidget(self.close_button)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.setFixedHeight(30)
        self.setStyleSheet("""
            TitleBar {
                background-color: #f8fafc;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        
        # 连接信号
        self.min_button.clicked.connect(self.parent.showMinimized)
        self.max_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(self.parent.close)
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 将事件传递给父窗口
            self.parent.moving = True
            self.parent.offset = event.globalPos() - self.parent.pos()
            
    def mouseMoveEvent(self, event):
        if self.parent.moving:
            # 使用全局坐标计算移动
            self.parent.move(event.globalPos() - self.parent.offset)
            
    def mouseReleaseEvent(self, event):
        # 重置父窗口的移动状态
        self.parent.moving = False
        self.parent.offset = None

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 外层布局（用于添加阴影边距）
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        # 容器widget（用于显示实际内容和阴影）
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # 内容布局
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        
        title_label = QLabel("配置")
        title_label.setStyleSheet("color: #333333; font-size: 13px;")
        
        close_button = QPushButton("×")
        close_button.setFixedSize(40, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #666666;
                font-family: Arial;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff4d4d;
                color: white;
            }
        """)
        close_button.clicked.connect(self.reject)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_button)
        
        # 内容区域
        content = QWidget()
        content.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        
        content_layout = QFormLayout(content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加说明标签
        description = QLabel(
            "设置图片路径前缀，用于处理相对路径的图片。\n"
            "• 全路径图片(如C:\\path\\to\\image.png)将直接处理\n"
            "• 相对路径图片将使用此前缀 + 相对路径进行处理"
        )
        description.setStyleSheet("color: #64748b; margin-bottom: 10px;")
        content_layout.addRow(description)
        
        # 图片路径前缀输入框
        self.path_prefix = QLineEdit()
        self.path_prefix.setPlaceholderText('例如: E:\\笔记\\Sherry\'s storehouse\\Z-附件')
        if parent and parent.image_path_prefix:
            self.path_prefix.setText(parent.image_path_prefix)
        
        content_layout.addRow('图片路径前缀:', self.path_prefix)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_btn = QPushButton('保存')
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d8ee6;
            }
            QPushButton:pressed {
                background-color: #3280d9;
            }
        """)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        content_layout.addRow('', button_layout)
        content.setLayout(content_layout)
        
        # 组装布局
        layout.addWidget(title_bar)
        layout.addWidget(content)
        
        # 添加阴影
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(20)
        effect.setXOffset(0)
        effect.setYOffset(0)
        effect.setColor(QColor(0, 0, 0, 50))
        container.setGraphicsEffect(effect)
        
        # 将容器添加到外层布局
        outer_layout.addWidget(container)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.moving and self.offset:
            self.move(event.globalPos() - self.offset)
            
    def mouseReleaseEvent(self, event):
        self.moving = False
        self.offset = None  # 重置 offset

class MainWindow(QMainWindow):
    def __init__(self, process_markdown_file, process_vault):
        super().__init__()
        self.process_markdown_file = process_markdown_file
        self.process_vault = process_vault
        self.moving = False
        self.offset = None
        self.image_path_prefix = ""
        self.initUI()

    def initUI(self):
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主容器
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加标题栏
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # 修改拖拽区域样式
        self.drop_area = DropArea(self)
        content_layout.addWidget(self.drop_area)

        # 修改按钮区域样式和布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 10, 0, 10)
        
        self.select_file_btn = QPushButton('选择文件')
        self.select_dir_btn = QPushButton('选择目录')
        self.wp_checkbox = QCheckBox('转换为WordPress图片链接')
        self.config_btn = QPushButton('配置')
        self.clear_log_btn = QPushButton('清空日志')
        
        # 连接按钮点击事件
        self.select_file_btn.clicked.connect(self.select_files)
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.config_btn.clicked.connect(self.show_config_dialog)
        
        # 设置按钮固定宽度和样式
        for btn in [self.select_file_btn, self.select_dir_btn]:
            btn.setFixedWidth(85)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #3d8ee6;
                }
                QPushButton:pressed {
                    background-color: #3280d9;
                }
            """)
        
        # 设置复选框样式
        self.wp_checkbox.setStyleSheet("""
            QCheckBox {
                margin-left: 10px;
            }
        """)
        
        # 设置配置按钮样式
        self.config_btn.setFixedWidth(85)
        self.config_btn.setFixedHeight(32)
        self.config_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        
        # 设置清空日志按钮样式
        self.clear_log_btn.setFixedWidth(85)
        self.clear_log_btn.setFixedHeight(32)
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.clear_log_btn.clicked.connect(self.clear_log)  # 确保连接了点击事件
        
        button_layout.addWidget(self.select_file_btn)
        button_layout.addWidget(self.select_dir_btn)
        button_layout.addWidget(self.wp_checkbox)
        button_layout.addWidget(self.config_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_log_btn)
        
        content_layout.addLayout(button_layout)

        # 修改日志显示区域样式
        self.log_display = LogDisplay()
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        self.log_display.setMinimumHeight(100)
        content_layout.addWidget(self.log_display)
        
        # 修改状态标签样式
        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
                padding: 5px;
            }
        """)
        content_layout.addWidget(self.status_label)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择Markdown文件",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )
        if files:
            self.handle_dropped_files(files)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择目录",
            ""
        )
        if directory:
            self.handle_dropped_files([directory])

    def log(self, text, level="info"):
        """
        添加日志并更新状态栏
        """
        self.log_display.append_log(text, level)
        if level == "error":
            self.status_label.setText("❌ " + text)
        elif level == "success":
            self.status_label.setText("✅ " + text)
        else:
            self.status_label.setText(text)

    def show_config_dialog(self):
        """显示配置对话框"""
        self.log("打开配置对话框...", "info")
        dialog = ConfigDialog(self)
        
        # 设置对话框大小
        dialog.setFixedSize(500, 300)
        
        # 计算对话框位置，使其在主窗口中心显示
        x = self.x() + (self.width() - dialog.width()) // 2
        y = self.y() + (self.height() - dialog.height()) // 2
        dialog.move(x, y)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            self.image_path_prefix = dialog.path_prefix.text().strip()
            self.log("已更新图片路径前缀配置 ✅", "success")

    def handle_dropped_files(self, paths):
        self.log("开始处理...", "info")
        try:
            convert_to_wp = self.wp_checkbox.isChecked()
            for path in paths:
                if os.path.isfile(path) and path.lower().endswith('.md'):
                    self.log(f"处理文件: {path}", "info")
                    self.process_markdown_file(path, convert_to_wp=convert_to_wp, 
                                            image_path_prefix=self.image_path_prefix)  # 传递前缀
                elif os.path.isdir(path):
                    self.log(f"处理目录: {path}", "info")
                    self.process_vault(path, convert_to_wp=convert_to_wp,
                                     image_path_prefix=self.image_path_prefix)  # 传递前缀
            self.log("处理完成！", "success")
        except Exception as e:
            self.log(f"处理出错: {str(e)}", "error")

    def clear_log(self):
        """
        清空日志显示区域
        """
        self.log_display.clear()
        self.status_label.setText('日志已清空')

    def initUI(self):
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建主容器
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加标题栏
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # 修改拖拽区域样式
        self.drop_area = DropArea(self)
        content_layout.addWidget(self.drop_area)

        # 修改按钮区域样式和布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 10, 0, 10)
        
        self.select_file_btn = QPushButton('选择文件')
        self.select_dir_btn = QPushButton('选择目录')
        self.wp_checkbox = QCheckBox('转换为WordPress图片链接')
        self.config_btn = QPushButton('配置')
        self.clear_log_btn = QPushButton('清空日志')
        
        # 连接按钮点击事件
        self.select_file_btn.clicked.connect(self.select_files)
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.config_btn.clicked.connect(self.show_config_dialog)
        
        # 设置按钮固定宽度和样式
        for btn in [self.select_file_btn, self.select_dir_btn]:
            btn.setFixedWidth(85)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #3d8ee6;
                }
                QPushButton:pressed {
                    background-color: #3280d9;
                }
            """)
        
        # 设置复选框样式
        self.wp_checkbox.setStyleSheet("""
            QCheckBox {
                margin-left: 10px;
            }
        """)
        
        # 设置配置按钮样式
        self.config_btn.setFixedWidth(85)
        self.config_btn.setFixedHeight(32)
        self.config_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        
        # 设置清空日志按钮样式
        self.clear_log_btn.setFixedWidth(85)
        self.clear_log_btn.setFixedHeight(32)
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        self.clear_log_btn.clicked.connect(self.clear_log)  # 确保连接了点击事件
        
        button_layout.addWidget(self.select_file_btn)
        button_layout.addWidget(self.select_dir_btn)
        button_layout.addWidget(self.wp_checkbox)
        button_layout.addWidget(self.config_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_log_btn)
        
        content_layout.addLayout(button_layout)

        # 修改日志显示区域样式
        self.log_display = LogDisplay()
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        self.log_display.setMinimumHeight(100)
        content_layout.addWidget(self.log_display)
        
        # 修改状态标签样式
        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
                padding: 5px;
            }
        """)
        content_layout.addWidget(self.status_label)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        container.setLayout(main_layout)
        self.setCentralWidget(container) 