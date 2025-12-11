import os
import re
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PyQt5.QtCore import QTimer

# 线程安全的打印函数
print_lock = threading.Lock()

# 全局变量存储UI引用
ui_window = None


def set_ui_window(window):
    global ui_window
    ui_window = window


def safe_print(*args, level="info"):
    """
    线程安全的打印函数，同时发送到UI
    """
    with print_lock:
        message = " ".join(map(str, args))
        print(message)
        if ui_window:
            # 使用 QTimer.singleShot 确保在主线程中更新UI
            QTimer.singleShot(0, lambda: ui_window.log(message, level))


def upload_image(image_path, max_retries=3):
    """
    上传图片到 PicGo
    """
    file_name = os.path.basename(image_path)

    for attempt in range(max_retries):
        try:
            picgo_url = "http://127.0.0.1:36677/upload"

            if not os.path.exists(image_path):
                safe_print(f"文件不存在: {file_name}", level="error")
                return None

            file_size = os.path.getsize(image_path)
            if file_size == 0:
                safe_print(f"文件大小为0: {file_name}", level="error")
                return None

            if attempt > 0:
                safe_print(
                    f"重试上传 ({attempt+1}/{max_retries}): {file_name}",
                    level="warning",
                )

            files = {"list": [image_path]}

            # 增加超时时间
            response = requests.post(picgo_url, json=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("result")[0]
                else:
                    safe_print(f"上传失败: {result.get('msg')}", level="error")
            else:
                safe_print(f"请求失败,状态码: {response.status_code}", level="error")

            if attempt < max_retries - 1:
                # 增加重试等待时间，并显示倒计时
                wait_time = 5
                safe_print(f"等待 {wait_time} 秒后重试...", level="warning")
                for i in range(wait_time, 0, -1):
                    safe_print(f"将在 {i} 秒后重试...", level="info")
                    time.sleep(1)

        except requests.Timeout:
            safe_print(
                f"上传超时，正在重试... ({attempt+1}/{max_retries})", level="warning"
            )
            if attempt < max_retries - 1:
                wait_time = 5
                safe_print(f"等待 {wait_time} 秒后重试...", level="warning")
                for i in range(wait_time, 0, -1):
                    safe_print(f"将在 {i} 秒后重试...", level="info")
                    time.sleep(1)

        except Exception as e:
            safe_print(f"上传错误: {str(e)}", level="error")
            if attempt < max_retries - 1:
                wait_time = 5
                safe_print(f"等待 {wait_time} 秒后重试...", level="warning")
                for i in range(wait_time, 0, -1):
                    safe_print(f"将在 {i} 秒后重试...", level="info")
                    time.sleep(1)

    safe_print(f"图片 {file_name} 上传失败", level="error")
    return None


def process_image_link(link, use_wordpress=False):
    """处理图片链接"""
    if use_wordpress:
        # 检查链接是否已经包含了 WordPress CDN 前缀
        wordpress_prefix = "//images.weserv.nl/?url="
        if not link.startswith(wordpress_prefix):
            return f"{wordpress_prefix}{link}"
    return link


def process_markdown_file(
    file_path,
    image_host=None,
    max_workers=3,
    convert_to_wp=False,
    remove_wp=False,
    image_path_prefix="",
):
    """
    处理单个markdown文件中的图片链接，使用线程池并行上传图片

    Args:
        file_path: Markdown文件路径
        image_host: 图床适配器实例
        max_workers: 最大工作线程数
        convert_to_wp: 是否转换为WordPress格式
        remove_wp: 是否移除WordPress前缀
        image_path_prefix: 图片路径前缀
    """
    from wordpress_processor import WordPressLinkProcessor

    file_name = os.path.basename(file_path)
    safe_print(f"处理文件: {file_name}", level="info")

    # 显示使用的图床服务
    if image_host:
        safe_print(f"使用图床: {image_host.get_name()}", level="info")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 匹配本地图片链接
        local_patterns = [
            # 普通格式：![...](C:\path\to\image.png)
            r"!\[.*?\]\(([A-Za-z]:\\[^)\n]+\.(?:png|jpg|jpeg|gif|bmp|PNG|JPG|JPEG|GIF|BMP))\)",
            # Obsidian格式：![[path/to/image.png]]
            r"!\[\[([^]\n]+\.(?:png|jpg|jpeg|gif|bmp|PNG|JPG|JPEG|GIF|BMP))\]\]",
        ]

        # 处理本地图片
        results = {}
        total_matches = []
        upload_count = 0

        for pattern in local_patterns:
            matches = list(re.finditer(pattern, content))
            total_matches.extend(matches)

        if total_matches:
            safe_print(f"发现 {len(total_matches)} 张图片需要上传", level="info")

            def upload_and_store(match):
                nonlocal upload_count
                try:
                    local_path = match.group(1)

                    # 处理 Obsidian 格式的路径 - 检查是否为绝对路径
                    if not (len(local_path) > 1 and local_path[1] == ":"):
                        if image_path_prefix:
                            local_path = os.path.join(image_path_prefix, local_path)
                        else:
                            base_dir = os.path.dirname(file_path)
                            local_path = os.path.join(base_dir, "Z-附件", local_path)

                    file_name = os.path.basename(local_path)

                    if os.path.exists(local_path):
                        safe_print(f"上传图片: {file_name}", level="info")

                        # 使用图床适配器上传
                        if image_host:
                            new_url = image_host.upload(local_path)
                        else:
                            # 回退到默认的PicGo上传
                            new_url = upload_image(local_path)

                        if new_url:
                            safe_print(f"图片 {file_name} 上传成功 ✅", level="success")
                            results[match.group(0)] = f"![]({new_url})"
                            upload_count += 1
                        else:
                            safe_print(f"图片 {file_name} 上传失败 ❌", level="error")
                    else:
                        safe_print(f"图片不存在: {file_name} ❌", level="error")
                except Exception as e:
                    safe_print(f"处理图片时出错: {str(e)} ❌", level="error")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(upload_and_store, total_matches)

            # 替换所有匹配的图片链接
            new_content = content
            for old_text, new_text in results.items():
                new_content = new_content.replace(old_text, new_text)

            if results:
                safe_print(f"已上传 {upload_count} 张图片 ✅", level="success")
        else:
            new_content = content
            safe_print("未发现需要上传的本地图片 ℹ️", level="info")

        # 处理WordPress链接
        wp_count = 0
        if convert_to_wp or remove_wp:
            new_content, wp_count = WordPressLinkProcessor.process_markdown_content(
                new_content, convert_to_wp=convert_to_wp, remove_wp=remove_wp
            )

            if wp_count > 0:
                if convert_to_wp:
                    safe_print(
                        f"已转换 {wp_count} 个链接为 WordPress 格式 ✅", level="success"
                    )
                elif remove_wp:
                    safe_print(f"已还原 {wp_count} 个 WordPress 链接 ✅", level="success")

        # 保存更新后的内容
        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            safe_print(f"文件已更新: {file_name} ✅", level="success")
        else:
            safe_print(f"文件未发生更改: {file_name} ℹ️", level="info")

    except FileNotFoundError as e:
        safe_print(f"文件未找到: {str(e)} ❌", level="error")
    except PermissionError as e:
        safe_print(f"权限不足: {str(e)} ❌", level="error")
    except UnicodeDecodeError as e:
        safe_print(f"文件编码错误: {str(e)} ❌", level="error")
    except Exception as e:
        safe_print(f"处理文件时发生错误: {str(e)} ❌", level="error")


def process_vault(
    path,
    image_host=None,
    max_workers=3,
    convert_to_wp=False,
    remove_wp=False,
    image_path_prefix="",
):
    """
    处理路径（可以是单个文件或目录）

    Args:
        path: 文件或目录路径
        image_host: 图床适配器实例
        max_workers: 最大工作线程数
        convert_to_wp: 是否转换为WordPress格式
        remove_wp: 是否移除WordPress前缀
        image_path_prefix: 图片路径前缀
    """
    try:
        path = Path(path)

        safe_print(f"处理路径: {path}", level="info")

        if path.is_file() and path.suffix.lower() == ".md":
            process_markdown_file(
                str(path),
                image_host=image_host,
                max_workers=max_workers,
                convert_to_wp=convert_to_wp,
                remove_wp=remove_wp,
                image_path_prefix=image_path_prefix,
            )
        elif path.is_dir():
            safe_print(f"开始处理目录: {path.name} 📁", level="info")
            md_files = list(path.rglob("*.md"))
            safe_print(f"发现 {len(md_files)} 个 Markdown 文件", level="info")
            for md_file in md_files:
                try:
                    process_markdown_file(
                        str(md_file),
                        image_host=image_host,
                        max_workers=max_workers,
                        convert_to_wp=convert_to_wp,
                        remove_wp=remove_wp,
                        image_path_prefix=image_path_prefix,
                    )
                except Exception as e:
                    safe_print(
                        f"处理文件 {md_file.name} 时出错: {str(e)} ❌", level="error"
                    )
                    # 继续处理其他文件
                    continue
            safe_print("所有文件处理完成！🎉", level="success")
        else:
            safe_print("请提供有效的markdown文件或目录路径 ⚠️", level="warning")
    except Exception as e:
        safe_print(f"处理路径时发生错误: {str(e)} ❌", level="error")


class ImageUploader:
    def __init__(self, api_url, token=None):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def upload(self, image_path):
        try:
            with open(image_path, "rb") as f:
                files = {"image": f}
                response = requests.post(
                    self.api_url, files=files, headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()["url"]  # 假设API返回JSON格式包含url字段
                else:
                    raise Exception(f"Upload failed: {response.text}")
        except Exception as e:
            raise Exception(f"Upload error: {str(e)}")
