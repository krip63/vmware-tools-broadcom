# VMware Tools 同步工具更新说明

## 🔍 官方目录结构详解

根据最新信息，`https://packages-prod.broadcom.com/tools/` 目录结构已更新，以下是关键目录说明：

### 📂 核心目录结构
```
📁 tools/
├── 📁 docs/             # 文档资源
├── 📁 esx/              # ESXi 相关工具
├── 📁 frozen/           # 遗留 VMware Tools（历史版本）
├── 📁 releases/         # 正式发布版本（重点目录）
└── 📁 ...               # 其他辅助目录
```

### 🚀 最新版 VMware Tools 位置
`releases/latest/` 目录包含最新版 VMware Tools（当前为 v13.0.0）

```
📁 releases/latest/
├── 📁 windows/          # Windows 平台工具
│   ├── 📁 x64/          # 64位安装程序
│   └── VMware-tools-windows-13.0.0-24696409.iso
├── 📁 linux/            # Linux 平台工具
├── 📁 macos/            # macOS 平台工具
├── 📁 repos/            # 仓库文件
└── 📁 ubuntu/           # Ubuntu 专用包
```

### ✅ Windows 平台文件示例
| 文件类型 | 路径 | 大小 |
|----------|------|------|
| ISO 镜像 | `releases/latest/windows/VMware-tools-windows-13.0.0-24696409.iso` | 112MB |
| 安装程序 | `releases/latest/windows/x64/VMware-tools-13.0.0-24696409-x64.exe` | 111MB |

### ⏳ 历史版本目录
`releases/` 目录包含从 v10.x 到 v13.0.0 的所有历史版本：
```
📁 releases/
├── 📁 v10.0.0/
├── 📁 v10.1.0/
├── ...
├── 📁 v12.0.0/
├── 📁 v12.5.0/
└── 📁 v13.0.0/
```

### ❄️ 遗留工具目录 (frozen)
包含旧平台支持文件：
```
📁 frozen/
├── 📁 darwin/     # macOS 旧版工具
├── 📁 linux/      # Linux 旧版工具
├── 📁 solaris/    # Solaris 工具
└── 📁 windows/    # Windows 旧版工具
    └── winPreVista.iso  # Windows Vista 之前版本
```

## 🆕 最新版本信息
- **版本号**: 13.0.0
- **构建号**: 24696409
- **发布日期**: 2025年6月18日
- **支持平台**: 
  - Windows (x86/x64)
  - Linux (各发行版)
  - macOS
  - Solaris
  - FreeBSD

## 💡 使用建议

### 1. 获取最新版本
```bash
# 同步整个目录（包含所有历史版本）
python sync_broadcom_tools.py

# 本地查看最新版
ls "VMware Tools/tools/releases/latest"
```

### 2. 直接下载最新版（不运行脚本）
- **Windows ISO**:  
  [https://packages-prod.broadcom.com/tools/releases/latest/windows/VMware-tools-windows-13.0.0-24696409.iso](https://packages-prod.broadcom.com/tools/releases/latest/windows/VMware-tools-windows-13.0.0-24696409.iso)

- **Linux 仓库**:  
  [https://packages-prod.broadcom.com/tools/releases/latest/linux/](https://packages-prod.broadcom.com/tools/releases/latest/linux/)

### 3. 特殊需求
- **历史版本**: 访问 `releases/v[版本号]/` 目录  
  示例: [https://packages-prod.broadcom.com/tools/releases/v12.5.0/](https://packages-prod.broadcom.com/tools/releases/v12.5.0/)

- **遗留系统支持**: 访问 `frozen/` 目录  
  示例: [https://packages-prod.broadcom.com/tools/frozen/windows/winPreVista.iso](https://packages-prod.broadcom.com/tools/frozen/windows/winPreVista.iso)

## 🔄 脚本更新说明
当前脚本已支持同步最新目录结构，无需修改即可获取：
1. 最新版 `releases/latest/`
2. 历史版本 `releases/vXX.X.X/`
3. 遗留工具 `frozen/`

```bash
# 同步后本地目录结构
📁 VMware Tools/
└── 📁 tools/
    ├── 📁 docs/
    ├── 📁 esx/
    ├── 📁 frozen/
    └── 📁 releases/
        ├── 📁 latest/
        ├── 📁 v10.0.0/
        ├── ...
        └── 📁 v13.0.0/
```

> **提示**：完整同步需要约 50GB 空间，若只需最新版，可手动下载 `releases/latest/` 内容

> **温馨提示**：本工具仅用于技术交流，请遵守Broadcom官方使用条款
