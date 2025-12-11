"""
腾讯云COS图床适配器
"""
import os
from typing import Dict, Any, List
from .base import ImageHostBase


class TencentCOSHost(ImageHostBase):
    """腾讯云COS图床适配器"""

    def upload(self, image_path: str) -> str:
        """
        上传图片到腾讯云COS

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        try:
            from qcloud_cos import CosConfig, CosS3Client
        except ImportError:
            raise Exception(
                "腾讯云COS SDK未安装，请运行: pip install cos-python-sdk-v5"
            )

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        secret_id = self.config["secret_id"]
        secret_key = self.config["secret_key"]
        region = self.config["region"]
        bucket = self.config["bucket"]

        # 配置COS客户端
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
        client = CosS3Client(config)

        # 生成对象键（文件名）
        file_name = os.path.basename(image_path)
        object_key = f"images/{file_name}"

        try:
            # 上传文件
            with open(image_path, "rb") as f:
                response = client.put_object(
                    Bucket=bucket, Body=f, Key=object_key, EnableMD5=False
                )

            # 构建URL
            url = f"https://{bucket}.cos.{region}.myqcloud.com/{object_key}"
            return url

        except Exception as e:
            raise Exception(f"腾讯云COS上传失败: {str(e)}")

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
        return ["secret_id", "secret_key", "bucket", "region"]
