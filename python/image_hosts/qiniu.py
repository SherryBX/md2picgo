"""
七牛云图床适配器
"""
import os
from typing import Dict, Any, List
from .base import ImageHostBase


class QiniuHost(ImageHostBase):
    """七牛云图床适配器"""

    def upload(self, image_path: str) -> str:
        """
        上传图片到七牛云

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        try:
            from qiniu import Auth, put_file
        except ImportError:
            raise Exception("七牛云SDK未安装，请运行: pip install qiniu")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        access_key = self.config["access_key"]
        secret_key = self.config["secret_key"]
        bucket_name = self.config["bucket"]
        domain = self.config["domain"]

        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传Token
        file_name = os.path.basename(image_path)
        key = f"images/{file_name}"
        token = q.upload_token(bucket_name, key, 3600)

        try:
            # 上传文件
            ret, info = put_file(token, key, image_path)

            if info.status_code == 200:
                # 构建URL
                url = f"http://{domain}/{key}"
                return url
            else:
                raise Exception(f"七牛云上传失败，状态码: {info.status_code}")

        except Exception as e:
            raise Exception(f"七牛云上传失败: {str(e)}")

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
        return ["access_key", "secret_key", "bucket", "domain"]
