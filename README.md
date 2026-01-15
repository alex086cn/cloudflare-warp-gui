# Cloudflare WARP GUI for Linux

[English](#english) | [中文简体](#中文简体)

---

<a name="english"></a>
## English

A lightweight, system tray-based graphical user interface for Cloudflare WARP on Linux (specifically optimized for Linux Mint Cinnamon).

### Features
- **Real-time Status Monitoring**: Tray icon changes color based on connection state (Green: Connected, Red: Disconnected, Orange: Connecting).
- **One-Click Control**: Quickly connect or disconnect WARP from the tray menu.
- **Protocol Switching**: Easily switch between **MASQUE** and **WireGuard** protocols.
- **Auto-Registration**: Automatically detects missing registrations and performs `warp-cli registration new` on startup.
- **Smart Monitoring**: Intelligent short-term polling after actions to ensure UI reflects the actual connection state without constant background noise.
- **Single Instance**: Prevents multiple tray icons by using a file lock mechanism.
- **Multi-language Support**: Automatically switches between **English** and **Simplified Chinese** based on system locale.
- **Clean Exit**: Forceful process group termination to ensure no tray icon residue.

### Installation
1. Ensure you have `cloudflare-warp` installed and the `warp-svc` daemon is running.
2. Clone this repository:
   ```bash
   git clone https://github.com/alex086cn/cloudflare-warp-gui.git
   cd cloudflare-warp-gui
   ```
3. Run the installation script:
   ```bash
   sudo ./install_warp_gui.sh
   ```
4. Find **"Cloudflare WARP GUI"** in your application menu and launch it.

---

<a name="中文简体"></a>
## 中文简体

一个轻量级的、基于系统托盘的 Cloudflare WARP Linux 图形用户界面（专门针对 Linux Mint Cinnamon 桌面环境进行了优化）。

### 核心功能
- **实时状态监控**：托盘图标根据连接状态改变颜色（绿色：已连接，红色：已断开，橙色：连接中）。
- **一键控制**：通过托盘菜单快速连接或断开 WARP。
- **协议切换**：在 **MASQUE** 和 **WireGuard** 协议之间轻松切换。
- **自动注册检测**：启动时自动检测注册状态，若缺失则自动执行 `warp-cli registration new`。
- **智能监控机制**：操作后进行短时间智能轮询，确保 UI 准确反映连接状态，平时保持静默以消除菜单抖动。
- **单例运行**：使用文件锁机制防止重复启动多个托盘图标。
- **多语言支持**：根据系统语言自动切换 **英文** 和 **简体中文**。
- **彻底退出**：采用强力进程组终止机制，确保退出时托盘图标无残留。

### 安装步骤
1. 请确保已安装 `cloudflare-warp` 且 `warp-svc` 守护进程正在运行。
2. 克隆此仓库：
   ```bash
   git clone https://github.com/alex086cn/cloudflare-warp-gui.git
   cd cloudflare-warp-gui
   ```
3. 运行安装脚本：
   ```bash
   sudo ./install_warp_gui.sh
   ```
4. 在应用菜单中搜索 **"Cloudflare WARP GUI"** 并启动。

## Requirements / 依赖要求
- Python 3.x
- `pystray`
- `Pillow`
- `python3-tk`
- `cloudflare-warp` (CLI client)

## License / 授权协议
MIT License
