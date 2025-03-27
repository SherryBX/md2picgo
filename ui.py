from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QFileDialog, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QColor, QTextCharFormat, QBrush
import os
import time

class DropArea(QLabel):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n将文件拖拽到此处\n或点击选择文件')
        self.setStyleSheet('''
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f0f0f0;
                min-height: 200px;
                font-size: 16px;
            }
        ''')
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet('''
                QLabel {
                    border: 2px dashed #3daee9;
                    border-radius: 5px;
                    background-color: #e3f3ff;
                    min-height: 200px;
                    font-size: 16px;
                }
            ''')

    def dragLeaveEvent(self, event):
        self.setStyleSheet('''
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f0f0f0;
                min-height: 200px;
                font-size: 16px;
            }
        ''')

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet('''
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f0f0f0;
                min-height: 200px;
                font-size: 16px;
            }
        ''')
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

class MainWindow(QMainWindow):
    def __init__(self, process_markdown_file, process_vault):
        super().__init__()
        self.process_markdown_file = process_markdown_file
        self.process_vault = process_vault
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Markdown 图片上传工具')
        self.setMinimumSize(800, 600)

        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建拖拽区域
        self.drop_area = DropArea(self)
        layout.addWidget(self.drop_area)

        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        self.select_file_btn = QPushButton('选择文件')
        self.select_file_btn.clicked.connect(self.select_files)
        
        self.select_dir_btn = QPushButton('选择目录')
        self.select_dir_btn.clicked.connect(self.select_directory)
        
        # 添加WordPress转换复选框
        self.wp_checkbox = QCheckBox('转换为WordPress图片链接')
        
        # 添加清空日志按钮
        self.clear_log_btn = QPushButton('清空日志')
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                color: #666;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #ccc;
            }
            QPushButton:pressed {
                background-color: #dde2e6;
            }
        """)
        
        button_layout.addWidget(self.select_file_btn)
        button_layout.addWidget(self.select_dir_btn)
        button_layout.addWidget(self.wp_checkbox)
        button_layout.addStretch()  # 添加弹性空间
        button_layout.addWidget(self.clear_log_btn)
        
        layout.addLayout(button_layout)

        # 添加日志显示区域
        self.log_display = LogDisplay()
        layout.addWidget(self.log_display)
        
        # 状态标签放在最下方
        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

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

    def handle_dropped_files(self, paths):
        self.log("开始处理...", "info")
        try:
            convert_to_wp = self.wp_checkbox.isChecked()
            for path in paths:
                if os.path.isfile(path) and path.lower().endswith('.md'):
                    self.log(f"处理文件: {path}", "info")
                    self.process_markdown_file(path, convert_to_wp=convert_to_wp)
                elif os.path.isdir(path):
                    self.log(f"处理目录: {path}", "info")
                    self.process_vault(path, convert_to_wp=convert_to_wp)
            self.log("处理完成！", "success")
        except Exception as e:
            self.log(f"处理出错: {str(e)}", "error")

    def clear_log(self):
        """
        清空日志显示区域
        """
        self.log_display.clear()
        self.status_label.setText('日志已清空') 