"""
Imgur图床适配器
"""
import os
import base64
import requests
from typing import Dict, Any, List
from .base import ImageHostBase


class ImgurHost(ImageHostBase):
    """Imgur图床适配器"""

    API_URL = "https://api.imgur.com/3/image"

    def upload(self, image_path: str) -> str:
        """
        上传图片到Imgur

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        client_id = self.config["client_id"]

        headers = {"Authorization": f"Client-ID {client_id}"}

        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            data = {"image": image_data, "type": "base64"}

            response = requests.post(
                self.API_URL, headers=headers, data=data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["data"]["link"]
                else:
                    raise Exception("Imgur upload failed")
            else:
                raise Exception(f"Imgur server error: {response.status_code}")

        except requests.Timeout:
            raise Exception("Imgur upload timeout")
        except requests.RequestException as e:
            raise Exception(f"Imgur request error: {str(e)}")

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
        return ["client_id"]
