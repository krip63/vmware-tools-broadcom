## Language Options

- [中文](README_CN.md)
- English

---

# VMware Tools Sync Utility Update Notes

## 🔍 Official Directory Structure Explained

According to the latest information, the structure under `https://packages-prod.broadcom.com/tools/` has been updated. Key directories are as follows:

### 📂 Core Directory Structure
```
📁 tools/
├── 📁 docs/             # Documentation resources
├── 📁 esx/              # ESXi related tools
├── 📁 frozen/           # Legacy VMware Tools (historical versions)
├── 📁 releases/         # Official releases (main directory)
└── 📁 ...               # Other auxiliary directories
```

### 🚀 Location of the Latest VMware Tools
The `releases/latest/` directory contains the most recent VMware Tools (currently v13.0.0):

```
📁 releases/latest/
├── 📁 windows/          # Windows tools
│   ├── 📁 x64/          # 64-bit installers
│   └── VMware-tools-windows-13.0.0-24696409.iso
├── 📁 linux/            # Linux tools
├── 📁 macos/            # macOS tools
├── 📁 repos/            # Repository files
└── 📁 ubuntu/           # Ubuntu-specific packages
```

### ✅ Example Windows Files
| File Type | Path | Size |
|-----------|------|------|
| ISO Image | `releases/latest/windows/VMware-tools-windows-13.0.0-24696409.iso` | 112MB |
| Installer | `releases/latest/windows/x64/VMware-tools-13.0.0-24696409-x64.exe` | 111MB |

### ⏳ Historical Versions Directory
The `releases/` directory contains all historical versions from v10.x to v13.0.0:
```
📁 releases/
├── 📁 v10.0.0/
├── 📁 v10.1.0/
├── ...
├── 📁 v12.0.0/
├── 📁 v12.5.0/
└── 📁 v13.0.0/
```

### ❄️ Legacy Tools Directory (frozen)
Contains files for older platforms:
```
📁 frozen/
├── 📁 darwin/     # Old macOS tools
├── 📁 linux/      # Old Linux tools
├── 📁 solaris/    # Solaris tools
└── 📁 windows/    # Old Windows tools
    └── winPreVista.iso  # For Windows versions before Vista
```

## 🆕 Latest Version Info
- **Version**: 13.0.0
- **Build Number**: 24696409
- **Release Date**: June 18, 2025
- **Supported Platforms**: 
  - Windows (x86/x64)
  - Linux (various distributions)
  - macOS
  - Solaris
  - FreeBSD

## 💡 Usage Suggestions

### 1. Get the Latest Version
```bash
# Sync the full directory (including all historical versions)
python sync_broadcom_tools.py

# Check the latest version locally
ls "VMware Tools/tools/releases/latest"
```

### 2. Download the Latest Version Directly (without script)
- **Windows ISO**:  
  [https://packages-prod.broadcom.com/tools/releases/latest/windows/VMware-tools-windows-13.0.0-24696409.iso](https://packages-prod.broadcom.com/tools/releases/latest/windows/VMware-tools-windows-13.0.0-24696409.iso)

- **Linux Repository**:  
  [https://packages-prod.broadcom.com/tools/releases/latest/linux/](https://packages-prod.broadcom.com/tools/releases/latest/linux/)

### 3. Special Requirements
- **Historical Versions**: Visit the `releases/v[version]/` directory  
  Example: [https://packages-prod.broadcom.com/tools/releases/v12.5.0/](https://packages-prod.broadcom.com/tools/releases/v12.5.0/)

- **Legacy System Support**: Visit the `frozen/` directory  
  Example: [https://packages-prod.broadcom.com/tools/frozen/windows/winPreVista.iso](https://packages-prod.broadcom.com/tools/frozen/windows/winPreVista.iso)

## 🔄 Script Update Notes
The current script supports syncing the latest directory structure, no modification needed to fetch:
1. Latest release `releases/latest/`
2. Historical versions `releases/vXX.X.X/`
3. Legacy tools `frozen/`

```bash
# Local directory structure after sync
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

> **Note**: A full sync requires about 50GB of space. If you only need the latest version, you can manually download content from `releases/latest/`.

> **Disclaimer**: This tool is intended solely for technical exchange. Please comply with Broadcom’s official terms of use.

![Win95截图](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/WIP_win95_1280x720?scl=1&fmt=png-alpha)


