"""
图床适配器包
"""
from .base import ImageHostBase
from .factory import ImageHostFactory
from .gitee import GiteeHost
from .tencent_cos import TencentCOSHost
from .aliyun_oss import AliyunOSSHost
from .smms import SMHost
from .github import GitHubHost
from .qiniu import QiniuHost
from .upyun import UpyunHost
from .imgur import ImgurHost

# 注册所有图床适配器
ImageHostFactory.register("gitee", GiteeHost)
ImageHostFactory.register("tencent_cos", TencentCOSHost)
ImageHostFactory.register("aliyun_oss", AliyunOSSHost)
ImageHostFactory.register("smms", SMHost)
ImageHostFactory.register("github", GitHubHost)
ImageHostFactory.register("qiniu", QiniuHost)
ImageHostFactory.register("upyun", UpyunHost)
ImageHostFactory.register("imgur", ImgurHost)

__all__ = [
    "ImageHostBase",
    "ImageHostFactory",
    "GiteeHost",
    "TencentCOSHost",
    "AliyunOSSHost",
    "SMHost",
    "GitHubHost",
    "QiniuHost",
    "UpyunHost",
    "ImgurHost",
]
