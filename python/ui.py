from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QTextEdit,
    QDialog,
    QLineEdit,
    QFormLayout,
    QGraphicsDropShadowEffect,
    QComboBox,
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QColor,
    QTextCharFormat,
    QBrush,
    QIcon,
)
import os
import time


class DropArea(QLabel):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAlignment(Qt.AlignCenter)
        self.setText("\n\n将文件拖拽到此处\n或点击选择文件")
        self.setFixedHeight(180)  # 固定高度
        self.setBaseStyle()
        self.setAcceptDrops(True)

    def setBaseStyle(self):
        """设置基础样式"""
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #4a9eff;
                border-radius: 8px;
                background-color: #f8fafc;
                font-size: 14px;
                color: #666666;
                min-width: 400px;  /* 添加最小宽度 */
            }
        """
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                """
                QLabel {
                    border: 2px dashed #3d8ee6;
                    border-radius: 8px;
                    background-color: #f0f7ff;
                    font-size: 14px;
                    color: #666666;
                    min-width: 400px;  /* 添加最小宽度 */
                }
            """
            )

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
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 8px;
            }
        """
        )

    def append_log(self, text, level="info"):
        """
        添加带颜色的日志
        level: info, success, error, warning
        """
        color_map = {
            "info": "#666666",  # 深灰色
            "success": "#2ecc71",  # 翠绿色
            "error": "#e74c3c",  # 红色
            "warning": "#f39c12",  # 橙色
        }

        # 添加时间戳
        timestamp = time.strftime("%H:%M:%S", time.localtime())

        # 添加等级图标
        level_icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(color_map.get(level, "#333333"))))

        self.moveCursor(self.textCursor().End)
        self.textCursor().insertText(
            f"[{timestamp}] {level_icons.get(level, '')} {text}\n", format
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
            btn.setStyleSheet(
                """
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
            """
            )

        self.close_button.setStyleSheet(
            """
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
        """
        )

        btn_layout.addWidget(self.min_button)
        btn_layout.addWidget(self.max_button)
        btn_layout.addWidget(self.close_button)

        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setFixedHeight(30)
        self.setStyleSheet(
            """
            TitleBar {
                background-color: #f8fafc;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """
        )

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
    # 图床配置字段定义
    IMAGE_HOST_FIELDS = {
        "gitee": [("服务器地址", "server", "http://127.0.0.1:36677")],
        "tencent_cos": [
            ("Secret ID", "secret_id", ""),
            ("Secret Key", "secret_key", ""),
            ("Bucket", "bucket", ""),
            ("Region", "region", "ap-guangzhou"),
        ],
        "aliyun_oss": [
            ("Access Key ID", "access_key_id", ""),
            ("Access Key Secret", "access_key_secret", ""),
            ("Bucket", "bucket", ""),
            ("Endpoint", "endpoint", "oss-cn-hangzhou.aliyuncs.com"),
        ],
        "smms": [("API Token", "token", "")],
        "github": [
            ("Token", "token", ""),
            ("Repository", "repo", "username/repo"),
            ("Branch", "branch", "main"),
            ("Path", "path", "images"),
        ],
        "qiniu": [
            ("Access Key", "access_key", ""),
            ("Secret Key", "secret_key", ""),
            ("Bucket", "bucket", ""),
            ("Domain", "domain", ""),
        ],
        "upyun": [
            ("Operator", "operator", ""),
            ("Password", "password", ""),
            ("Bucket", "bucket", ""),
            ("Domain", "domain", ""),
        ],
        "imgur": [("Client ID", "client_id", "")],
    }

    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.host_config_widgets = {}
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        # 外层布局
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        # 容器widget
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(
            """
            #container {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }
        """
        )

        # 内容布局
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)

        # 内容区域
        content = self.create_content()
        layout.addWidget(content)

        # 添加阴影
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(20)
        effect.setXOffset(0)
        effect.setYOffset(0)
        effect.setColor(QColor(0, 0, 0, 50))
        container.setGraphicsEffect(effect)

        outer_layout.addWidget(container)

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet(
            """
            QWidget {
                background-color: #f8fafc;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """
        )

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)

        title_label = QLabel("配置")
        title_label.setStyleSheet("color: #333333; font-size: 13px;")

        close_button = QPushButton("×")
        close_button.setFixedSize(40, 30)
        close_button.setStyleSheet(
            """
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
        """
        )
        close_button.clicked.connect(self.reject)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_button)

        return title_bar

    def create_content(self):
        content = QWidget()
        content.setStyleSheet(
            """
            QWidget {
                background-color: white;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """
        )

        content_layout = QFormLayout(content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # 图床选择
        self.image_host_combo = QComboBox()
        self.image_host_combo.addItems(
            [
                "Gitee",
                "腾讯云COS",
                "阿里云OSS",
                "SM.MS",
                "GitHub",
                "七牛云",
                "又拍云",
                "Imgur",
            ]
        )
        self.image_host_combo.currentIndexChanged.connect(self.on_image_host_changed)
        content_layout.addRow("图床类型:", self.image_host_combo)

        # 图床配置容器（固定高度）
        self.host_config_container = QWidget()
        self.host_config_container.setMinimumHeight(200)  # 设置最小高度
        self.host_config_container.setMaximumHeight(200)  # 设置最大高度
        self.host_config_layout = QFormLayout(self.host_config_container)
        self.host_config_layout.setSpacing(10)
        content_layout.addRow(self.host_config_container)

        # WordPress选项（互斥）
        self.wp_convert_checkbox = QCheckBox("转换为WordPress图片链接")
        self.wp_convert_checkbox.stateChanged.connect(self.on_wp_convert_changed)
        content_layout.addRow("WordPress:", self.wp_convert_checkbox)

        self.wp_remove_checkbox = QCheckBox("去除WordPress链接前缀")
        self.wp_remove_checkbox.stateChanged.connect(self.on_wp_remove_changed)
        content_layout.addRow("", self.wp_remove_checkbox)

        # 图片路径前缀
        self.path_prefix = QLineEdit()
        self.path_prefix.setPlaceholderText("例如: E:\\笔记\\附件")
        content_layout.addRow("图片路径前缀:", self.path_prefix)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet(
            """
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
        """
        )

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(
            """
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
        """
        )

        save_btn.clicked.connect(self.save_config)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        content_layout.addRow("", button_layout)

        return content

    def on_wp_convert_changed(self, state):
        """WordPress转换选项改变时"""
        if state and self.wp_remove_checkbox.isChecked():
            self.wp_remove_checkbox.setChecked(False)

    def on_wp_remove_changed(self, state):
        """WordPress去除选项改变时"""
        if state and self.wp_convert_checkbox.isChecked():
            self.wp_convert_checkbox.setChecked(False)

    def on_image_host_changed(self, index):
        # 清除现有配置字段
        while self.host_config_layout.count():
            item = self.host_config_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.host_config_widgets.clear()

        # 获取图床类型
        host_types = [
            "gitee",
            "tencent_cos",
            "aliyun_oss",
            "smms",
            "github",
            "qiniu",
            "upyun",
            "imgur",
        ]
        host_type = host_types[index]

        # 添加对应的配置字段
        if host_type in self.IMAGE_HOST_FIELDS:
            for label, key, placeholder in self.IMAGE_HOST_FIELDS[host_type]:
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(placeholder)
                if key == "password":
                    line_edit.setEchoMode(QLineEdit.Password)
                self.host_config_layout.addRow(f"{label}:", line_edit)
                self.host_config_widgets[key] = line_edit

    def load_config(self):
        if not self.config_manager:
            return

        # 加载图床配置
        image_host_config = self.config_manager.get_image_host_config()
        host_type = image_host_config.get("type", "gitee")

        host_types = [
            "gitee",
            "tencent_cos",
            "aliyun_oss",
            "smms",
            "github",
            "qiniu",
            "upyun",
            "imgur",
        ]
        if host_type in host_types:
            self.image_host_combo.setCurrentIndex(host_types.index(host_type))

        # 加载图床具体配置
        host_config = image_host_config.get("config", {})
        for key, widget in self.host_config_widgets.items():
            if key in host_config:
                widget.setText(str(host_config[key]))

        # 加载WordPress配置
        wp_config = self.config_manager.get_wordpress_config()
        self.wp_convert_checkbox.setChecked(wp_config.get("enabled", False))
        self.wp_remove_checkbox.setChecked(wp_config.get("remove_prefix", False))

        # 加载路径前缀
        self.path_prefix.setText(self.config_manager.get_image_path_prefix())

    def save_config(self):
        if not self.config_manager:
            self.accept()
            return

        # 保存图床配置
        host_types = [
            "gitee",
            "tencent_cos",
            "aliyun_oss",
            "smms",
            "github",
            "qiniu",
            "upyun",
            "imgur",
        ]
        host_type = host_types[self.image_host_combo.currentIndex()]

        host_config = {}
        for key, widget in self.host_config_widgets.items():
            value = widget.text().strip()
            if value:
                host_config[key] = value

        self.config_manager.update_image_host(host_type, host_config)

        # 保存WordPress配置
        self.config_manager.update_wordpress(
            self.wp_convert_checkbox.isChecked(), self.wp_remove_checkbox.isChecked()
        )

        # 保存路径前缀
        self.config_manager.update_image_path_prefix(self.path_prefix.text().strip())

        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving and self.offset:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.moving = False
        self.offset = None


class MainWindow(QMainWindow):
    def __init__(self, process_markdown_file, process_vault, config_manager=None):
        super().__init__()
        self.setWindowIcon(QIcon("icon/hello kitty.ico"))  # 设置窗口图标
        self.process_markdown_file = process_markdown_file
        self.process_vault = process_vault
        self.config_manager = config_manager
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
        container.setStyleSheet(
            """
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """
        )

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

        self.select_file_btn = QPushButton("选择文件")
        self.select_dir_btn = QPushButton("选择目录")
        self.config_btn = QPushButton("配置")
        self.clear_log_btn = QPushButton("清空日志")

        # 状态显示标签
        self.status_info_label = QLabel()
        self.status_info_label.setStyleSheet("color: #64748b; font-size: 12px;")
        self.update_status_info()

        # 连接按钮点击事件
        self.select_file_btn.clicked.connect(self.select_files)
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.config_btn.clicked.connect(self.show_config_dialog)

        # 设置按钮固定宽度和样式
        for btn in [self.select_file_btn, self.select_dir_btn]:
            btn.setFixedWidth(85)
            btn.setFixedHeight(32)
            btn.setStyleSheet(
                """
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
            """
            )

        # 设置配置按钮样式
        self.config_btn.setFixedWidth(85)
        self.config_btn.setFixedHeight(32)
        self.config_btn.setStyleSheet(
            """
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
        """
        )

        # 设置清空日志按钮样式
        self.clear_log_btn.setFixedWidth(85)
        self.clear_log_btn.setFixedHeight(32)
        self.clear_log_btn.setStyleSheet(
            """
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
        """
        )
        self.clear_log_btn.clicked.connect(self.clear_log)  # 确保连接了点击事件

        button_layout.addWidget(self.select_file_btn)
        button_layout.addWidget(self.select_dir_btn)
        button_layout.addWidget(self.status_info_label)
        button_layout.addStretch()
        button_layout.addWidget(self.config_btn)
        button_layout.addWidget(self.clear_log_btn)

        content_layout.addLayout(button_layout)

        # 修改日志显示区域样式
        self.log_display = LogDisplay()
        self.log_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """
        )
        self.log_display.setMinimumHeight(100)
        content_layout.addWidget(self.log_display)

        # 修改状态标签样式
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #64748b;
                font-size: 12px;
                padding: 5px;
            }
        """
        )
        content_layout.addWidget(self.status_label)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)

        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择Markdown文件", "", "Markdown Files (*.md);;All Files (*)"
        )
        if files:
            self.handle_dropped_files(files)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录", "")
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

    def update_status_info(self):
        """更新状态信息显示"""
        if not self.config_manager:
            self.status_info_label.setText("图床: PicGo")
            return

        # 获取图床类型
        image_host_config = self.config_manager.get_image_host_config()
        host_type = image_host_config.get("type", "picgo")

        host_names = {
            "gitee": "Gitee",
            "tencent_cos": "腾讯云COS",
            "aliyun_oss": "阿里云OSS",
            "smms": "SM.MS",
            "github": "GitHub",
            "qiniu": "七牛云",
            "upyun": "又拍云",
            "imgur": "Imgur",
        }

        host_name = host_names.get(host_type, "未知")

        # 获取WordPress状态
        wp_config = self.config_manager.get_wordpress_config()
        wp_status = ""
        if wp_config.get("enabled"):
            wp_status = " | WP转换: 开"
        elif wp_config.get("remove_prefix"):
            wp_status = " | WP去除: 开"

        self.status_info_label.setText(f"图床: {host_name}{wp_status}")

    def show_config_dialog(self):
        """显示配置对话框"""
        self.log("打开配置对话框...", "info")
        dialog = ConfigDialog(self, self.config_manager)

        # 设置对话框大小
        dialog.setFixedSize(600, 500)

        # 计算对话框位置，使其在主窗口中心显示
        x = self.x() + (self.width() - dialog.width()) // 2
        y = self.y() + (self.height() - dialog.height()) // 2
        dialog.move(x, y)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            if self.config_manager:
                self.image_path_prefix = self.config_manager.get_image_path_prefix()
            self.update_status_info()
            self.log("配置已更新 ✅", "success")

    def handle_dropped_files(self, paths):
        self.log("开始处理...", "info")
        try:
            # 从配置管理器获取WordPress选项
            wp_config = (
                self.config_manager.get_wordpress_config()
                if self.config_manager
                else {"enabled": False, "remove_prefix": False}
            )
            convert_to_wp = wp_config.get("enabled", False)
            remove_wp = wp_config.get("remove_prefix", False)

            for path in paths:
                if os.path.isfile(path) and path.lower().endswith(".md"):
                    self.log(f"处理文件: {path}", "info")
                    self.process_markdown_file(
                        path,
                        convert_to_wp=convert_to_wp,
                        remove_wp=remove_wp,
                        image_path_prefix=self.image_path_prefix,
                    )
                elif os.path.isdir(path):
                    self.log(f"处理目录: {path}", "info")
                    self.process_vault(
                        path,
                        convert_to_wp=convert_to_wp,
                        remove_wp=remove_wp,
                        image_path_prefix=self.image_path_prefix,
                    )
            self.log("处理完成！", "success")
        except Exception as e:
            self.log(f"处理出错: {str(e)}", "error")

    def clear_log(self):
        """
        清空日志显示区域
        """
        self.log_display.clear()
        self.status_label.setText("日志已清空")
