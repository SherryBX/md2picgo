"""
图床工厂类
根据配置创建对应的图床适配器实例
"""
from typing import Dict, Any
from .base import ImageHostBase


class ImageHostFactory:
    """图床工厂类"""

    _registry: Dict[str, type] = {}

    @classmethod
    def register(cls, host_type: str, host_class: type):
        """
        注册图床适配器类

        Args:
            host_type: 图床类型标识
            host_class: 图床适配器类
        """
        cls._registry[host_type] = host_class

    @classmethod
    def create(cls, host_type: str, config: Dict[str, Any]) -> ImageHostBase:
        """
        创建图床适配器实例

        Args:
            host_type: 图床类型
            config: 图床配置

        Returns:
            图床适配器实例

        Raises:
            ValueError: 不支持的图床类型
        """
        if host_type not in cls._registry:
            raise ValueError(f"Unsupported image host type: {host_type}")

        host_class = cls._registry[host_type]
        return host_class(config)

    @classmethod
    def get_supported_types(cls) -> list:
        """
        获取支持的图床类型列表

        Returns:
            支持的图床类型列表
        """
        return list(cls._registry.keys())
