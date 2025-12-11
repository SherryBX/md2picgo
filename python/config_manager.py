"""
配置管理模块
负责配置的加载、保存和验证
"""
import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器类"""

    DEFAULT_CONFIG = {
        "image_host": {"type": "gitee", "config": {"server": "http://127.0.0.1:36677"}},
        "wordpress": {"enabled": False, "remove_prefix": False},
        "image_path_prefix": "",
        "max_workers": 3,
        "max_retries": 3,
    }

    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        从文件加载配置

        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            # 配置文件不存在，使用默认配置
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 验证配置
            if self.validate_config(config):
                # 合并默认配置，确保所有必需字段都存在
                merged_config = self.DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            else:
                print("配置文件格式错误，使用默认配置")
                return self.DEFAULT_CONFIG.copy()

        except json.JSONDecodeError as e:
            print(f"配置文件JSON格式错误: {e}，使用默认配置")
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"加载配置文件时出错: {e}，使用默认配置")
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存配置到文件

        Args:
            config: 要保存的配置字典，如果为None则保存当前配置

        Returns:
            是否保存成功
        """
        if config is None:
            config = self.config

        try:
            # 验证配置
            if not self.validate_config(config):
                print("配置验证失败，无法保存")
                return False

            # 保存到文件
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # 更新内存中的配置
            self.config = config
            return True

        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            return False

    def get_image_host_config(self) -> Dict[str, Any]:
        """
        获取图床配置

        Returns:
            图床配置字典
        """
        return self.config.get("image_host", self.DEFAULT_CONFIG["image_host"])

    def get_wordpress_config(self) -> Dict[str, bool]:
        """
        获取WordPress配置

        Returns:
            WordPress配置字典
        """
        return self.config.get("wordpress", self.DEFAULT_CONFIG["wordpress"])

    def get_image_path_prefix(self) -> str:
        """
        获取图片路径前缀

        Returns:
            图片路径前缀
        """
        return self.config.get("image_path_prefix", "")

    def get_max_workers(self) -> int:
        """
        获取最大工作线程数

        Returns:
            最大工作线程数
        """
        return self.config.get("max_workers", 3)

    def get_max_retries(self) -> int:
        """
        获取最大重试次数

        Returns:
            最大重试次数
        """
        return self.config.get("max_retries", 3)

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置的有效性

        Args:
            config: 要验证的配置字典

        Returns:
            配置是否有效
        """
        try:
            # 检查必需的顶级字段
            if "image_host" not in config:
                return False

            # 检查图床配置
            image_host = config["image_host"]
            if not isinstance(image_host, dict):
                return False

            if "type" not in image_host or "config" not in image_host:
                return False

            # 检查WordPress配置（如果存在）
            if "wordpress" in config:
                wordpress = config["wordpress"]
                if not isinstance(wordpress, dict):
                    return False

            # 检查数值类型字段
            if "max_workers" in config:
                if not isinstance(config["max_workers"], int) or config["max_workers"] < 1:
                    return False

            if "max_retries" in config:
                if not isinstance(config["max_retries"], int) or config["max_retries"] < 1:
                    return False

            return True

        except Exception:
            return False

    def update_image_host(self, host_type: str, host_config: Dict[str, Any]) -> bool:
        """
        更新图床配置

        Args:
            host_type: 图床类型
            host_config: 图床配置

        Returns:
            是否更新成功
        """
        self.config["image_host"] = {"type": host_type, "config": host_config}
        return self.save_config()

    def update_wordpress(self, enabled: bool, remove_prefix: bool = False) -> bool:
        """
        更新WordPress配置

        Args:
            enabled: 是否启用WordPress转换
            remove_prefix: 是否移除WordPress前缀

        Returns:
            是否更新成功
        """
        self.config["wordpress"] = {"enabled": enabled, "remove_prefix": remove_prefix}
        return self.save_config()

    def update_image_path_prefix(self, prefix: str) -> bool:
        """
        更新图片路径前缀

        Args:
            prefix: 图片路径前缀

        Returns:
            是否更新成功
        """
        self.config["image_path_prefix"] = prefix
        return self.save_config()
