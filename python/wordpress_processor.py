"""
WordPress链接处理模块
处理WordPress链接的转换和还原
"""
import re
from typing import Optional


class WordPressLinkProcessor:
    """WordPress链接处理器"""

    WORDPRESS_PREFIX = "//images.weserv.nl/?url="

    @staticmethod
    def convert_to_wordpress(url: str) -> str:
        """
        将URL转换为WordPress格式

        Args:
            url: 原始URL

        Returns:
            WordPress格式的URL
        """
        # 如果已经是WordPress链接，直接返回
        if WordPressLinkProcessor.is_wordpress_link(url):
            return url

        # 移除URL开头的协议前缀（如果有）
        clean_url = url
        if url.startswith("http://"):
            clean_url = url[7:]
        elif url.startswith("https://"):
            clean_url = url[8:]

        # 添加WordPress前缀
        return f"{WordPressLinkProcessor.WORDPRESS_PREFIX}{clean_url}"

    @staticmethod
    def remove_wordpress_prefix(url: str) -> str:
        """
        移除WordPress前缀，还原为原始URL

        Args:
            url: WordPress格式的URL

        Returns:
            原始URL
        """
        if not WordPressLinkProcessor.is_wordpress_link(url):
            return url

        # 移除WordPress前缀
        original_url = url.replace(WordPressLinkProcessor.WORDPRESS_PREFIX, "", 1)

        # 如果原始URL不包含协议，添加https://
        if not original_url.startswith(("http://", "https://", "//")):
            original_url = f"https://{original_url}"

        return original_url

    @staticmethod
    def is_wordpress_link(url: str) -> bool:
        """
        判断URL是否为WordPress链接

        Args:
            url: 要检查的URL

        Returns:
            是否为WordPress链接
        """
        return url.startswith(WordPressLinkProcessor.WORDPRESS_PREFIX)

    @staticmethod
    def process_markdown_content(
        content: str, convert_to_wp: bool = False, remove_wp: bool = False
    ) -> tuple[str, int]:
        """
        处理Markdown内容中的图片链接

        Args:
            content: Markdown内容
            convert_to_wp: 是否转换为WordPress格式
            remove_wp: 是否移除WordPress前缀

        Returns:
            (处理后的内容, 处理的链接数量)
        """
        # 匹配Markdown图片链接：![alt](url)
        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        matches = list(re.finditer(pattern, content))

        if not matches:
            return content, 0

        processed_count = 0
        new_content = content

        for match in matches:
            full_match = match.group(0)
            alt_text = match.group(1)
            url = match.group(2)

            new_url = url
            should_replace = False

            if convert_to_wp and not WordPressLinkProcessor.is_wordpress_link(url):
                # 转换为WordPress格式
                new_url = WordPressLinkProcessor.convert_to_wordpress(url)
                should_replace = True
            elif remove_wp and WordPressLinkProcessor.is_wordpress_link(url):
                # 移除WordPress前缀
                new_url = WordPressLinkProcessor.remove_wordpress_prefix(url)
                should_replace = True

            if should_replace:
                new_image_mark = f"![{alt_text}]({new_url})"
                new_content = new_content.replace(full_match, new_image_mark, 1)
                processed_count += 1

        return new_content, processed_count
