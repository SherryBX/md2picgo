import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from uploader import process_markdown_file, process_vault, set_ui_window

def main():
    app = QApplication(sys.argv)
    window = MainWindow(process_markdown_file, process_vault)
    set_ui_window(window)  # 设置UI引用
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
