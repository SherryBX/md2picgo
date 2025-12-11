"""
图床适配器基类
定义所有图床适配器的接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class ImageHostBase(ABC):
    """图床适配器抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化图床适配器

        Args:
            config: 图床配置字典
        """
        self.config = config
        if not self.validate_config(config):
            raise ValueError(f"Invalid configuration for {self.__class__.__name__}")

    @abstractmethod
    def upload(self, image_path: str) -> str:
        """
        上传图片到图床

        Args:
            image_path: 图片本地路径

        Returns:
            上传后的图片URL

        Raises:
            Exception: 上传失败时抛出异常
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效

        Args:
            config: 配置字典

        Returns:
            配置是否有效
        """
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """
        获取必需的配置字段列表

        Returns:
            必需字段名称列表
        """
        pass

    def get_name(self) -> str:
        """
        获取图床名称

        Returns:
            图床名称
        """
        return self.__class__.__name__.replace("Host", "")
