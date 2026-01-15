# Cloudflare WARP GUI for Linux

A lightweight, system tray-based graphical user interface for Cloudflare WARP on Linux (specifically optimized for Linux Mint Cinnamon).

## Features

- **Real-time Status Monitoring**: Tray icon changes color based on connection state (Green: Connected, Red: Disconnected, Orange: Connecting).
- **One-Click Control**: Quickly connect or disconnect WARP from the tray menu.
- **Protocol Switching**: Easily switch between **MASQUE** and **WireGuard** protocols.
- **Auto-Registration**: Automatically detects missing registrations and performs `warp-cli registration new` on startup.
- **Smart Monitoring**: Intelligent short-term polling after actions to ensure UI reflects the actual connection state without constant background noise.
- **Single Instance**: Prevents multiple tray icons by using a file lock mechanism.
- **Multi-language Support**: Automatically switches between **English** and **Simplified Chinese** based on system locale.
- **Clean Exit**: Forceful process group termination to ensure no tray icon residue.

## Installation

1. Ensure you have `cloudflare-warp` installed and the `warp-svc` daemon is running.
2. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cloudflare-warp-gui.git
   cd cloudflare-warp-gui
   ```
3. Run the installation script:
   ```bash
   sudo ./install_warp_gui.sh
   ```
4. Find **"Cloudflare WARP GUI"** in your application menu and launch it.

## Requirements

- Python 3.x
- `pystray`
- `Pillow`
- `python3-tk` (for some UI elements)
- `cloudflare-warp` (CLI client)

## License

MIT License
