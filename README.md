
# VMware Tools 同步工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

此工具用于自动同步 Broadcom 官方提供的 VMware Tools 资源，支持增量更新和高效下载。资源来源自官方接口：

`https://packages-prod.broadcom.com/tools/`

## 🚀 功能特点

- 🔄 **增量同步**：仅下载更新的文件，节省时间和带宽
- ⚡ **多线程下载**：自动根据 CPU 核心数优化下载速度（最高16线程）
- 📝 **详细日志**：记录所有操作和性能指标
- 🛡️ **错误恢复**：自动重试失败下载（可配置重试次数）
- ⏱️ **时间戳同步**：保持文件修改时间与服务器一致
- 🖥️ **跨平台支持**：兼容 Windows、Linux 和 macOS
- 📦 **智能更新检测**：通过文件大小、修改时间和 ETag 三重验证
- 🛠️ **命令行配置**：支持自定义线程数、重试策略等参数

## 📥 获取脚本

1. 克隆仓库：
```bash
git clone https://github.com/1564307973/vmware-tools-broadcom.git
cd vmware-tools-broadcom
```

2. 安装依赖：
```bash
pip install requests beautifulsoup4
```

## 🚀 使用说明

### 基本命令
```bash
python sync_broadcom_tools.py
```

### 首次运行（完全同步）
```bash
python sync_broadcom_tools.py --full-sync
```

### 高级选项
```bash
# 指定本地目录和日志文件
python sync_broadcom_tools.py --local-dir /path/to/sync --log-file /path/to/sync.log

# 设置线程数
python sync_broadcom_tools.py --threads 8

# 自定义重试参数
python sync_broadcom_tools.py --retries 5 --delay 3
```

## ⚙️ 命令行参数

| 参数 | 缩写 | 默认值 | 描述 |
|------|------|---------|------|
| `--local-dir` | `-d` | `VMware Tools/tools` | 本地存储目录 |
| `--log-file` | `-l` | `vmware_tools_sync.log` | 日志文件路径 |
| `--threads` | `-t` | 自动设置 | 下载线程数 |
| `--retries` | `-r` | `3` | 下载失败重试次数 |
| `--delay` | `-w` | `5` | 重试延迟时间（秒） |
| `--full-sync` | `-f` | `False` | 强制完全同步（忽略本地文件） |

## 📊 日志示例

```
2023-10-15 14:30:22 - INFO - 🚀 开始 VMware Tools 同步
2023-10-15 14:30:22 - INFO - 🖥️ 系统: Windows 10 (AMD64)
2023-10-15 14:30:22 - INFO - 💻 CPU: 8 核心
2023-10-15 14:30:22 - INFO - 📁 本地目录: C:\VMware Tools\tools
2023-10-15 14:30:22 - INFO - 📝 日志文件: C:\logs\vmware_tools_sync.log

2023-10-15 14:30:24 - INFO - 🔍 检查文件: windows.iso
2023-10-15 14:30:24 - INFO -   本地大小: 52428800 | 远程大小: 52428800
2023-10-15 14:30:24 - INFO -   文件未变更

2023-10-15 14:30:24 - INFO - 🔍 检查文件: linux.iso
2023-10-15 14:30:24 - INFO -   本地大小: 41943040 | 远程大小: 44564480
2023-10-15 14:30:24 - INFO -   文件大小变化: 41943040 → 44564480
2023-10-15 14:30:24 - INFO - ⬇️ 开始下载: https://packages-prod.broadcom.com/tools/vmware-tools/linux.iso
2023-10-15 14:31:05 - INFO - ✅ 下载完成: https://packages-prod.broadcom.com/tools/vmware-tools/linux.iso
2023-10-15 14:31:05 - INFO -   大小: 42.50 MB | 用时: 40.22秒 | 速度: 1.06 MB/s

2023-10-15 14:31:05 - INFO - ✅ 同步完成! 用时: 42.85 秒
2023-10-15 14:31:05 - INFO - 📊 统计:
2023-10-15 14:31:05 - INFO -   总文件数: 24
2023-10-15 14:31:05 - INFO -   需要下载: 1
2023-10-15 14:31:05 - INFO -   成功下载: 1
2023-10-15 14:31:05 - INFO -   下载失败: 0
```

## ⚠️ 注意事项

1. **存储空间**：确保本地存储有足够的空间（建议至少 50GB）
2. **网络连接**：稳定的网络连接可提高下载成功率
3. **首次运行**：首次同步建议使用 `--full-sync` 参数
4. **定时任务**：可设置定时任务定期同步更新
   ```bash
   # Linux/macOS 定时任务（每天凌晨3点）
   0 3 * * * /usr/bin/python3 /path/to/sync_broadcom_tools.py
   
   # Windows 计划任务（使用任务计划程序）
   ```

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：
1. Fork 项目仓库
2. 创建新分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -am 'Add some feature'`)
4. 推送分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 📞 支持

如有问题，请提交 [Issue](https://github.com/1564307973/vmware-tools-broadcom/issues)

