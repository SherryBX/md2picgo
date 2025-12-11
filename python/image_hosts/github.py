"""
GitHub图床适配器
"""
import os
import base64
import requests
from typing import Dict, Any, List
from .base import ImageHostBase


class GitHubHost(ImageHostBase):
    """GitHub图床适配器"""

    API_BASE = "https://api.github.com"

    def upload(self, image_path: str) -> str:
        """
        上传图片到GitHub

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        token = self.config["token"]
        repo = self.config["repo"]
        branch = self.config.get("branch", "main")
        path_prefix = self.config.get("path", "images")

        # 读取文件并编码为base64
        with open(image_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        # 生成文件路径
        file_name = os.path.basename(image_path)
        file_path = f"{path_prefix}/{file_name}".strip("/")

        # 构建API URL
        api_url = f"{self.API_BASE}/repos/{repo}/contents/{file_path}"

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 构建请求数据
        data = {
            "message": f"Upload {file_name}",
            "content": content,
            "branch": branch,
        }

        try:
            response = requests.put(api_url, json=data, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                result = response.json()
                # 返回raw内容URL
                download_url = result["content"]["download_url"]
                return download_url
            else:
                error_msg = response.json().get("message", "Unknown error")
                raise Exception(f"GitHub upload failed: {error_msg}")

        except requests.Timeout:
            raise Exception("GitHub upload timeout")
        except requests.RequestException as e:
            raise Exception(f"GitHub request error: {str(e)}")

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效

        Args:
            config: 配置字典

        Returns:
            配置是否有效
        """
        required_fields = ["token", "repo"]
        for field in required_fields:
            if field not in config or not config[field]:
                return False
        return True

    def get_required_fields(self) -> List[str]:
        """
        获取必需的配置字段列表

        Returns:
            必需字段名称列表
        """
        return ["token", "repo", "branch", "path"]
