"""
SM.MS图床适配器
"""
import os
import requests
from typing import Dict, Any, List
from .base import ImageHostBase


class SMHost(ImageHostBase):
    """SM.MS图床适配器"""

    API_URL = "https://sm.ms/api/v2/upload"

    def upload(self, image_path: str) -> str:
        """
        上传图片到SM.MS

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        token = self.config.get("token", "")

        headers = {}
        if token:
            headers["Authorization"] = token

        try:
            with open(image_path, "rb") as f:
                files = {"smfile": f}
                response = requests.post(
                    self.API_URL, files=files, headers=headers, timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["data"]["url"]
                else:
                    error_msg = result.get("message", "Unknown error")
                    raise Exception(f"SM.MS upload failed: {error_msg}")
            else:
                raise Exception(f"SM.MS server error: {response.status_code}")

        except requests.Timeout:
            raise Exception("SM.MS upload timeout")
        except requests.RequestException as e:
            raise Exception(f"SM.MS request error: {str(e)}")

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

        # token是可选的
        if "token" in config:
            if not isinstance(config["token"], str):
                return False

        return True

    def get_required_fields(self) -> List[str]:
        """
        获取必需的配置字段列表

        Returns:
            必需字段名称列表
        """
        return []  # token是可选的
