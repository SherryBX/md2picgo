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
                safe_print(f"重试上传 ({attempt+1}/{max_retries}): {file_name}", level="warning")
            
            files = {
                'list': [image_path]
            }
            
            # 增加超时时间
            response = requests.post(picgo_url, json=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('result')[0]
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
            safe_print(f"上传超时，正在重试... ({attempt+1}/{max_retries})", level="warning")
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

def process_markdown_file(file_path, max_workers=3, convert_to_wp=False, image_path_prefix=""):
    """
    处理单个markdown文件中的图片链接，使用线程池并行上传图片
    """
    file_name = os.path.basename(file_path)
    safe_print(f"处理文件: {file_name}", level="info")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配本地图片链接
        local_patterns = [
            # 普通格式：![...](C:\path\to\image.png)
            r'!\[.*?\]\(([A-Z]:\\[^)\n]+\.(?:png|jpg|jpeg|gif|bmp))\)?',
            # Obsidian格式：![[path/to/image.png]]
            r'!\[\[([^]\n]+\.(?:png|jpg|jpeg|gif|bmp))\]\]'
        ]
        
        # 处理本地图片
        results = {}
        total_matches = []
        
        for pattern in local_patterns:
            matches = list(re.finditer(pattern, content))
            total_matches.extend(matches)
        
        if total_matches:
            safe_print(f"发现 {len(total_matches)} 张图片需要上传", level="info")
            
            def upload_and_store(match):
                local_path = match.group(1)
                
                # 处理 Obsidian 格式的路径
                if not local_path.startswith(('C:', 'D:', 'E:')):
                    if image_path_prefix:
                        local_path = os.path.join(image_path_prefix, local_path)
                    else:
                        base_dir = os.path.dirname(file_path)
                        local_path = os.path.join(base_dir, 'Z-附件', local_path)
                
                file_name = os.path.basename(local_path)
                
                if os.path.exists(local_path):
                    safe_print(f"上传图片: {file_name}", level="info")
                    new_url = upload_image(local_path)
                    if new_url:
                        if convert_to_wp:
                            new_url = "//images.weserv.nl/?url=" + new_url
                        safe_print(f"图片 {file_name} 上传成功 ✅", level="success")
                        results[match.group(0)] = f'![]({new_url})'
                    else:
                        safe_print(f"图片 {file_name} 上传失败 ❌", level="error")
                else:
                    safe_print(f"图片不存在: {file_name} ❌", level="error")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(upload_and_store, total_matches)

            # 替换所有匹配的图片链接
            new_content = content
            for old_text, new_text in results.items():
                new_content = new_content.replace(old_text, new_text)
            
            if results:
                safe_print(f"已替换 {len(results)} 个图片链接 ✅", level="success")
        else:
            new_content = content
            safe_print("未发现需要上传的本地图片 ℹ️", level="info")

        # 处理已上传的 Gitee 图片链接
        if convert_to_wp:
            gitee_matches = list(re.finditer(gitee_pattern, new_content))
            if gitee_matches:
                safe_print(f"转换 {len(gitee_matches)} 个 Gitee 链接为 WordPress 格式 🔄", level="info")
                for match in gitee_matches:
                    gitee_url = match.group(1)
                    wp_url = "//images.weserv.nl/?url=" + gitee_url
                    new_content = new_content.replace(gitee_url, wp_url)

        # 保存更新后的内容
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            safe_print(f"文件已更新: {file_name} ✅", level="success")
        else:
            safe_print(f"文件未发生更改: {file_name} ℹ️", level="info")
            
    except Exception as e:
        safe_print(f"处理文件时发生错误: {str(e)} ❌", level="error")

def process_vault(path, convert_to_wp=False, image_path_prefix=""):
    """
    处理路径（可以是单个文件或目录）
    """
    path = Path(path)
    
    if path.is_file() and path.suffix.lower() == '.md':
        process_markdown_file(str(path), convert_to_wp=convert_to_wp, 
                            image_path_prefix=image_path_prefix)
    elif path.is_dir():
        safe_print(f"开始处理目录: {path.name} 📁", level="info")
        md_files = list(path.rglob('*.md'))
        safe_print(f"发现 {len(md_files)} 个 Markdown 文件", level="info")
        for md_file in md_files:
            process_markdown_file(str(md_file), convert_to_wp=convert_to_wp,
                               image_path_prefix=image_path_prefix)
        safe_print("所有文件处理完成！🎉", level="success")
    else:
        safe_print("请提供有效的markdown文件或目录路径 ⚠️", level="warning")

class ImageUploader:
    def __init__(self, api_url, token=None):
        self.api_url = api_url
        self.headers = {'Authorization': f'Bearer {token}'} if token else {}
        
    def upload(self, image_path):
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(self.api_url, 
                                      files=files,
                                      headers=self.headers)
                if response.status_code == 200:
                    return response.json()['url']  # 假设API返回JSON格式包含url字段
                else:
                    raise Exception(f'Upload failed: {response.text}')
        except Exception as e:
            raise Exception(f'Upload error: {str(e)}') 