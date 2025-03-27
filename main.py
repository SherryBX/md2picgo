import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui import MainWindow
from uploader import process_markdown_file, process_vault, set_ui_window

def main():
    app = QApplication(sys.argv)
    # 设置应用程序图标
    icon = QIcon('icon/hello kitty.ico')
    app.setWindowIcon(icon)
    
    window = MainWindow(process_markdown_file, process_vault)
    window.setWindowIcon(icon)  # 设置窗口图标
    set_ui_window(window)  # 设置UI引用
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
