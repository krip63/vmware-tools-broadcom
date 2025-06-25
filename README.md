# 🛠️ VMware Tools Broadcom 同步脚本
该项目用于 **增量同步** Broadcom 官方网站 [https://packages-prod.broadcom.com/tools/](https://packages-prod.broadcom.com/tools/) 上的 `tools` 文件夹内容，文件保存到本地固定目录 `VMware Tools/tools/`，同名文件自动覆盖，方便备份和版本管理。
---
## ⚙️ 功能说明
- 🔄 **递归下载** `tools` 目录下所有文件和子目录  
- 📂 保持远程目录结构，文件存储于 `VMware Tools/tools/`  
- 🔁 同名文件自动覆盖，实现增量更新  
- ⚠️ 错误自动捕获，打印错误日志  
- 🚫 不删除本地多余文件，避免误删  
---
## 📅 自动更新（GitHub Actions）
本仓库包含 GitHub Action 工作流，可每周自动运行脚本，自动提交更新。
---
## 📜 许可证
MIT License
---
## 联系
如有问题欢迎提 issue 或联系作者。
---
*Powered by Python 🐍 & GitHub Actions 🤖*


