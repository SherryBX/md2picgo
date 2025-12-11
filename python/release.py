"""
GitHub发布脚本
自动创建GitHub Release并上传exe文件
"""
import os
import sys
import subprocess
import json

def check_git_repo():
    """检查是否在git仓库中"""
    try:
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        return True
    except:
        print("❌ 错误: 当前目录不是git仓库")
        return False

def get_version():
    """获取版本号"""
    version = input("请输入版本号 (例如: v2.0.0): ").strip()
    if not version:
        version = "v2.0.0"
    if not version.startswith('v'):
        version = 'v' + version
    return version

def git_commit_and_push(version):
    """提交代码并推送到GitHub"""
    print("\n提交代码到GitHub...")
    
    try:
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 提交
        commit_msg = f"Release {version}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # 推送
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ 代码已推送到GitHub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        return False

def create_github_release(version):
    """创建GitHub Release"""
    print(f"\n创建GitHub Release {version}...")
    
    # 检查是否安装了gh CLI
    try:
        subprocess.run(['gh', '--version'], check=True, capture_output=True)
    except:
        print("❌ 错误: 未安装GitHub CLI (gh)")
        print("请访问 https://cli.github.com/ 安装")
        return False
    
    # 创建release
    try:
        release_notes = f"""
## 🎉 md2picgo {version}

### ✨ 主要特性
- 🌐 支持8个主流图床服务（Gitee、腾讯云COS、阿里云OSS、SM.MS、GitHub、七牛云、又拍云、Imgur）
- 🔌 WordPress链接转换和还原功能
- ⚙️ 灵活的配置管理系统
- 🎨 优雅的图形界面
- 🔄 批量处理和多线程上传

### 📦 安装说明
1. 下载 md2picgo.exe
2. 双击运行
3. 点击"配置"设置图床信息
4. 开始使用！

### 📝 更新日志
详见 [CHANGELOG.md](https://github.com/你的用户名/md2picgo/blob/main/python/CHANGELOG.md)
"""
        
        cmd = [
            'gh', 'release', 'create', version,
            '--title', f'md2picgo {version}',
            '--notes', release_notes
        ]
        
        # 如果有exe文件，添加到release
        exe_path = 'dist/md2picgo.exe'
        if os.path.exists(exe_path):
            cmd.append(exe_path)
            print(f"将上传文件: {exe_path}")
        
        subprocess.run(cmd, check=True)
        print(f"✅ GitHub Release {version} 创建成功！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建Release失败: {e}")
        return False

def main():
    print("=" * 50)
    print("md2picgo GitHub发布工具")
    print("=" * 50)
    
    # 检查git仓库
    if not check_git_repo():
        return
    
    # 检查exe文件
    if not os.path.exists('dist/md2picgo.exe'):
        print("❌ 错误: 未找到 dist/md2picgo.exe")
        print("请先运行 python build.py 打包程序")
        return
    
    # 获取版本号
    version = get_version()
    print(f"\n版本号: {version}")
    
    # 确认
    confirm = input("\n是否继续发布到GitHub? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 提交并推送代码
    if not git_commit_and_push(version):
        return
    
    # 创建GitHub Release
    if create_github_release(version):
        print("\n🎉 发布成功！")
        print(f"\n访问 GitHub 查看 Release: https://github.com/你的用户名/md2picgo/releases")
    else:
        print("\n❌ 发布失败！")

if __name__ == "__main__":
    main()
