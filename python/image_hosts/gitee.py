"""
Gitee图床适配器
"""
import os
import requests
from typing import Dict, Any, List
from .base import ImageHostBase


class GiteeHost(ImageHostBase):
    """Gitee图床适配器"""

    def upload(self, image_path: str) -> str:
        """
        上传图片到Gitee

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        server = self.config.get("server", "http://127.0.0.1:36677")
        upload_url = f"{server}/upload"

        files = {"list": [image_path]}

        try:
            response = requests.post(upload_url, json=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("result")[0]
                else:
                    raise Exception(f"Gitee upload failed: {result.get('msg')}")
            else:
                raise Exception(f"Gitee server error: {response.status_code}")

        except requests.Timeout:
            raise Exception("Gitee upload timeout")
        except requests.RequestException as e:
            raise Exception(f"Gitee request error: {str(e)}")

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效

        Args:
            config: 配置字典

        Returns:
            配置是否有效
        """
        if not isinstance(config, dict):
            return False

        # server字段是可选的，有默认值
        if "server" in config:
            server = config["server"]
            if not isinstance(server, str) or not server.startswith("http"):
                return False

        return True

    def get_required_fields(self) -> List[str]:
        """
        获取必需的配置字段列表

        Returns:
            必需字段名称列表
        """
        return []  # server是可选的，有默认值
