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
    上传图片到 PicGo，失败时最多重试3次
    """
    for attempt in range(max_retries):
        try:
            picgo_url = "http://127.0.0.1:36677/upload"
            
            if not os.path.exists(image_path):
                safe_print(f"文件不存在: {image_path}")
                return None
                
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                safe_print(f"文件大小为0: {image_path}")
                return None
                
            safe_print(f"正在上传图片 (第{attempt + 1}次尝试): {image_path} (大小: {file_size} 字节)")
                
            files = {
                'list': [image_path]
            }
            
            try:
                response = requests.post(picgo_url, json=files, timeout=10)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('success'):
                            return result.get('result')[0]
                        else:
                            safe_print(f"上传失败: {result.get('msg')}")
                            if attempt < max_retries - 1:
                                safe_print(f"将在3秒后进行第{attempt + 2}次尝试...")
                                time.sleep(3)
                                continue
                    except ValueError as e:
                        safe_print(f"JSON 解析错误: {e}")
                        if attempt < max_retries - 1:
                            safe_print(f"将在3秒后进行第{attempt + 2}次尝试...")
                            time.sleep(3)
                            continue
                else:
                    safe_print(f"请求失败,状态码: {response.status_code}")
                    if attempt < max_retries - 1:
                        safe_print(f"将在3秒后进行第{attempt + 2}次尝试...")
                        time.sleep(3)
                        continue
                    
            except requests.exceptions.RequestException as e:
                safe_print(f"请求异常: {e}")
                if attempt < max_retries - 1:
                    safe_print(f"将在3秒后进行第{attempt + 2}次尝试...")
                    time.sleep(3)
                    continue
                
        except Exception as e:
            safe_print(f"上传过程发生错误: {e}")
            if attempt < max_retries - 1:
                safe_print(f"将在3秒后进行第{attempt + 2}次尝试...")
                time.sleep(3)
                continue
    
    safe_print(f"已达到最大重试次数({max_retries}次)，上传失败")
    return None

def process_markdown_file(file_path, max_workers=3, convert_to_wp=False):
    """
    处理单个markdown文件中的图片链接，使用线程池并行上传图片
    """
    safe_print(f"正在处理文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配本地图片和已上传的 Gitee 图片
        local_pattern = r'!\[.*?\]\(([A-Z]:\\[^)\n]+\.(?:png|jpg|jpeg|gif|bmp))\)?'
        gitee_pattern = r'!\[.*?\]\((https://gitee\.com/[^)\n]+)\)?'
        
        # 处理本地图片
        local_matches = list(re.finditer(local_pattern, content))
        results = {}
        
        if local_matches:
            def upload_and_store(match):
                local_path = match.group(1)
                safe_print(f"\n开始处理图片: {local_path}")
                
                if os.path.exists(local_path):
                    new_url = upload_image(local_path)
                    if new_url:
                        if convert_to_wp:
                            new_url = "//images.weserv.nl/?url=" + new_url
                        safe_print(f"上传成功，新URL: {new_url}")
                        results[local_path] = new_url
                    else:
                        safe_print(f"上传失败，保持原链接")
                        results[local_path] = None
                else:
                    safe_print(f"图片不存在: {local_path}")
                    results[local_path] = None

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(upload_and_store, local_matches)

            # 替换本地图片链接
            new_content = content
            for match in local_matches:
                local_path = match.group(1)
                if local_path in results and results[local_path]:
                    new_content = new_content.replace(match.group(0), f'![]({results[local_path]})')
        else:
            new_content = content

        # 处理已上传的 Gitee 图片链接
        if convert_to_wp:
            gitee_matches = list(re.finditer(gitee_pattern, new_content))
            for match in gitee_matches:
                gitee_url = match.group(1)
                wp_url = "//images.weserv.nl/?url=" + gitee_url
                new_content = new_content.replace(gitee_url, wp_url)

        # 保存更新后的内容
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            safe_print(f"\n文件已更新: {file_path}")
        else:
            safe_print(f"\n文件未发生更改: {file_path}")
            
    except Exception as e:
        safe_print(f"处理文件时发生错误: {str(e)}")

def process_vault(path, convert_to_wp=False):
    """
    处理路径（可以是单个文件或目录）
    convert_to_wp: 是否转换为WordPress支持的图片链接格式
    """
    path = Path(path)
    
    if path.is_file() and path.suffix.lower() == '.md':
        process_markdown_file(str(path), convert_to_wp=convert_to_wp)
    elif path.is_dir():
        safe_print(f"开始处理目录: {path}")
        for md_file in path.rglob('*.md'):
            process_markdown_file(str(md_file), convert_to_wp=convert_to_wp)
        safe_print("所有文件处理完成！")
    else:
        safe_print("请提供有效的markdown文件或目录路径") 