import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui import MainWindow
from uploader import set_ui_window
from config_manager import ConfigManager
from image_hosts import ImageHostFactory


def create_process_functions(config_manager):
    """创建处理函数，使用配置管理器"""

    def process_markdown_file(
        file_path, convert_to_wp=False, remove_wp=False, image_path_prefix=""
    ):
        from uploader import process_markdown_file as _process_markdown_file

        # 获取图床配置
        image_host_config = config_manager.get_image_host_config()
        host_type = image_host_config.get("type", "gitee")
        host_config = image_host_config.get("config", {})

        # 创建图床实例
        try:
            image_host = ImageHostFactory.create(host_type, host_config)
        except Exception as e:
            print(f"创建图床实例失败: {e}，使用默认Gitee")
            image_host = None

        # 调用处理函数
        _process_markdown_file(
            file_path,
            image_host=image_host,
            max_workers=config_manager.get_max_workers(),
            convert_to_wp=convert_to_wp,
            remove_wp=remove_wp,
            image_path_prefix=image_path_prefix,
        )

    def process_vault(
        path, convert_to_wp=False, remove_wp=False, image_path_prefix=""
    ):
        from uploader import process_vault as _process_vault

        # 获取图床配置
        image_host_config = config_manager.get_image_host_config()
        host_type = image_host_config.get("type", "gitee")
        host_config = image_host_config.get("config", {})

        # 创建图床实例
        try:
            image_host = ImageHostFactory.create(host_type, host_config)
        except Exception as e:
            print(f"创建图床实例失败: {e}，使用默认Gitee")
            image_host = None

        # 调用处理函数
        _process_vault(
            path,
            image_host=image_host,
            max_workers=config_manager.get_max_workers(),
            convert_to_wp=convert_to_wp,
            remove_wp=remove_wp,
            image_path_prefix=image_path_prefix,
        )

    return process_markdown_file, process_vault


def main():
    app = QApplication(sys.argv)

    # 设置应用程序图标（修正路径）
    icon_path = r"icon\hello kitty.ico"
    app.setWindowIcon(QIcon(icon_path))

    # 初始化配置管理器
    config_manager = ConfigManager("config.json")

    # 创建处理函数
    process_markdown_file, process_vault = create_process_functions(config_manager)

    # 创建主窗口
    window = MainWindow(process_markdown_file, process_vault, config_manager)
    window.setWindowIcon(QIcon(icon_path))  # 设置窗口图标
    set_ui_window(window)  # 设置UI引用

    # 从配置加载图片路径前缀
    window.image_path_prefix = config_manager.get_image_path_prefix()

    # 显式设置任务栏图标
    import ctypes

    myappid = "sherry.md2picgo.1.0"  # 任意字符串，作为应用程序ID
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
