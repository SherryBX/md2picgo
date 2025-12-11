"""
阿里云OSS图床适配器
"""
import os
from typing import Dict, Any, List
from .base import ImageHostBase


class AliyunOSSHost(ImageHostBase):
    """阿里云OSS图床适配器"""

    def upload(self, image_path: str) -> str:
        """
        上传图片到阿里云OSS

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL
        """
        try:
            import oss2
        except ImportError:
            raise Exception("阿里云OSS SDK未安装，请运行: pip install oss2")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        access_key_id = self.config["access_key_id"]
        access_key_secret = self.config["access_key_secret"]
        endpoint = self.config["endpoint"]
        bucket_name = self.config["bucket"]

        # 创建认证对象
        auth = oss2.Auth(access_key_id, access_key_secret)

        # 创建Bucket对象
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 生成对象键（文件名）
        file_name = os.path.basename(image_path)
        object_key = f"images/{file_name}"

        try:
            # 上传文件
            result = bucket.put_object_from_file(object_key, image_path)

            if result.status == 200:
                # 构建URL
                url = f"https://{bucket_name}.{endpoint}/{object_key}"
                return url
            else:
                raise Exception(f"阿里云OSS上传失败，状态码: {result.status}")

        except Exception as e:
            raise Exception(f"阿里云OSS上传失败: {str(e)}")

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
        return ["access_key_id", "access_key_secret", "bucket", "endpoint"]
