# 🚀 Obsidian-to-PicGo

> 🎨 一个优雅的 Obsidian 图片上传工具 | Made with ❤️ by Sherry

## ✨ 特性

- 🖼️ 自动将 Obsidian 中的本地图片上传至图床
- 🔄 支持批量处理整个文件夹
- 🎯 支持拖拽上传文件
- 🌈 多线程并行上传，效率更高
- 🎨 优雅的日志显示界面
- 🔌 支持转换为 WordPress 图片链接格式
- 🔄 上传失败自动重试
- 📝 保持原有 Markdown 格式

## 💡 链接转换说明

程序会自动处理以下两种情况：
    
    - 本地图片链接 → 图床链接
    - 已有图床链接 → WordPress 链接

## 🚀 快速开始

1. 确保已安装 [PicGo](https://github.com/Molunerfinn/PicGo) 并配置好图床
2. 运行程序：
```bash
python main.py
```

## 🛠️ 使用方法

1. 拖拽 Markdown 文件或文件夹到程序窗口
2. 点击"选择文件"或"选择目录"按钮选择要处理的文件
3. 如需转换为 WordPress 格式，请勾选对应选项
4. 等待上传完成即可

## 🎨 界面预览

![程序界面](界面截图链接)

## 🔧 依赖

- Python 3.6+
- PyQt5
- requests

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🌟 特别说明

- 支持的图片格式：png, jpg, jpeg, gif, bmp
- 需要 PicGo 在后台运行（默认端口：36677）
- 建议在处理前备份重要文件
- 支持批量处理整个 Obsidian 仓库
- 自动识别并处理所有本地图片链接
- WordPress 链接转换功能可选

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可

MIT License © 2025 Sherry

## 🎉 致谢

- [PicGo](https://github.com/Molunerfinn/PicGo) - 优秀的图床工具
- [Obsidian](https://obsidian.md/) - 强大的知识管理工具

---

> 🎨 **Sherry's Notes**: 希望这个小工具能让你的写作流程更加顺畅！如果觉得有帮助，欢迎给个 Star ⭐️

