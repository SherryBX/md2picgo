"""
又拍云图床适配器
"""
import os
import hashlib
import requests
from typing import Dict, Any, List
from .base import ImageHostBase


class UpyunHost(ImageHostBase):
    """又拍云图床适配器"""

    def upload(self, image_path: str) -> str:
        """
        上传图片到又拍云

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        operator = self.config["operator"]
        password = self.config["password"]
        bucket = self.config["bucket"]
        domain = self.config["domain"]

        # 生成文件路径
        file_name = os.path.basename(image_path)
        remote_path = f"/images/{file_name}"

        # 构建上传URL
        upload_url = f"http://v0.api.upyun.com/{bucket}{remote_path}"

        # 生成密码MD5
        password_md5 = hashlib.md5(password.encode()).hexdigest()

        # 构建认证头
        headers = {"Authorization": f"Basic {operator}:{password_md5}"}

        try:
            with open(image_path, "rb") as f:
                response = requests.put(
                    upload_url, data=f, headers=headers, timeout=30
                )

            if response.status_code == 200:
                # 构建URL
                url = f"http://{domain}{remote_path}"
                return url
            else:
                raise Exception(f"又拍云上传失败，状态码: {response.status_code}")

        except requests.Timeout:
            raise Exception("又拍云上传超时")
        except requests.RequestException as e:
            raise Exception(f"又拍云请求错误: {str(e)}")

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效

        Args:
            config: 配置字典

        Returns:
            配置是否有效
        """
        required_fields = self.get_required_fields()
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
        return ["operator", "password", "bucket", "domain"]
