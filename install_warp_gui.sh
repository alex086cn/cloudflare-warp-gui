#!/bin/bash

# 检查是否以 sudo 运行
if [ "$EUID" -ne 0 ]; then
  echo "请使用 sudo 运行此脚本以安装依赖项。"
  exit 1
fi

# 获取实际执行 sudo 的用户名
REAL_USER=$SUDO_USER
if [ -z "$REAL_USER" ]; then
    REAL_USER=$(whoami)
fi

# 获取该用户的家目录
REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)

echo "正在为用户 $REAL_USER 安装依赖..."
apt update
apt install -y python3-pip python3-pil python3-pystray python3-tk

# 创建程序目录
INSTALL_DIR="$REAL_HOME/.local/share/warp-gui"
sudo -u "$REAL_USER" mkdir -p "$INSTALL_DIR"

# 复制脚本并设置权限
cp warp_gui.py "$INSTALL_DIR/main.py"
chown "$REAL_USER:$REAL_USER" "$INSTALL_DIR/main.py"
chmod +x "$INSTALL_DIR/main.py"

# 创建桌面启动器目录
APP_DIR="$REAL_HOME/.local/share/applications"
sudo -u "$REAL_USER" mkdir -p "$APP_DIR"

# 创建桌面启动器文件
DESKTOP_FILE="$APP_DIR/warp-gui.desktop"
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=Cloudflare WARP GUI
Comment=Manage Cloudflare WARP connection
Exec=python3 $INSTALL_DIR/main.py
Icon=network-vpn
Terminal=false
Type=Application
Categories=Network;
EOF

# 设置启动器权限
chown "$REAL_USER:$REAL_USER" "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"

# 添加到自启动
AUTOSTART_DIR="$REAL_HOME/.config/autostart"
sudo -u "$REAL_USER" mkdir -p "$AUTOSTART_DIR"
cp "$DESKTOP_FILE" "$AUTOSTART_DIR/"
chown "$REAL_USER:$REAL_USER" "$AUTOSTART_DIR/$(basename "$DESKTOP_FILE")"

# 刷新桌面数据库
update-desktop-database "$APP_DIR"

echo "--------------------------------------------------"
echo "安装完成！"
echo "1. 您现在可以在应用菜单中搜索 'Cloudflare WARP GUI' 启动。"
echo "2. 如果菜单中没出现，请尝试注销并重新登录。"
echo "3. 您也可以手动运行以下命令启动测试："
echo "   python3 $INSTALL_DIR/main.py"
echo "--------------------------------------------------"
