import os
import subprocess
import threading
import time
import locale
import re
import sys
import signal
import fcntl
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# 多语言配置
LANG_DATA = {
    'zh_CN': {
        'status': '状态',
        'connected': '已连接',
        'disconnected': '已断开',
        'connecting': '连接中',
        'needs_reg': '需要注册',
        'registering': '正在注册...',
        'cli_not_found': '未找到 CLI',
        'connect': '连接',
        'disconnect': '断开',
        'protocol': '协议切换',
        'reset_settings': '恢复默认设置',
        'quit': '退出',
        'mode': '模式',
        'proto': '当前协议'
    },
    'en_US': {
        'status': 'Status',
        'connected': 'Connected',
        'disconnected': 'Disconnected',
        'connecting': 'Connecting',
        'needs_reg': 'Needs Registration',
        'registering': 'Registering...',
        'cli_not_found': 'CLI Not Found',
        'connect': 'Connect',
        'disconnect': 'Disconnect',
        'protocol': 'Switch Protocol',
        'reset_settings': 'Reset to Default',
        'quit': 'Quit',
        'mode': 'Mode',
        'proto': 'Protocol'
    }
}

class WarpGUI:
    def __init__(self):
        self.lang = self.get_system_lang()
        self.t = LANG_DATA.get(self.lang, LANG_DATA['en_US'])
        
        self.status_raw = "Disconnected"
        self.status_display = self.t['disconnected']
        self.mode = "Unknown"
        self.protocol = "Unknown"
        self.icon = None
        self.running = True
        self._monitor_thread = None
        
        # 锁文件路径
        self.lock_file_path = os.path.expanduser("~/.warp_gui.lock")
        self.lock_file = None

    def check_single_instance(self):
        """使用文件锁确保单例运行"""
        try:
            self.lock_file = open(self.lock_file_path, 'w')
            fcntl.lockf(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            return False

    def get_system_lang(self):
        try:
            lang = locale.getdefaultlocale()[0]
            if lang and lang.startswith('zh'):
                return 'zh_CN'
        except:
            pass
        return 'en_US'
        
    def run_shell_command(self, cmd_str):
        try:
            result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return ""

    def check_and_register(self):
        """增强的注册状态检查，适配详细的错误输出"""
        status_out = self.run_shell_command("warp-cli status")
        if re.search(r"Registration\s+Missing", status_out, re.IGNORECASE) or \
           re.search(r"not\s+registered", status_out, re.IGNORECASE) or \
           "Unable" in status_out:
            print(f"Detection triggered: Registration missing or status unable. Output: {status_out}")
            self.run_shell_command("warp-cli registration new")
            time.sleep(1.5)
            # 注册后立即触发一次状态更新，并启动短时监控以应对自动连接
            self.update_warp_state()
            self.start_short_term_monitor()
            return True
        return False

    def update_warp_state(self):
        # 1. 获取连接状态
        status_out = self.run_shell_command("warp-cli status")
        if "Connected" in status_out:
            self.status_raw = "Connected"
            self.status_display = self.t['connected']
        elif "Connecting" in status_out:
            self.status_raw = "Connecting"
            self.status_display = self.t['connecting']
        elif re.search(r"Registration\s+Missing", status_out, re.IGNORECASE):
            self.status_raw = "Disconnected"
            self.status_display = self.t['needs_reg']
        else:
            self.status_raw = "Disconnected"
            self.status_display = self.t['disconnected']

        # 2. 获取设置信息 (模式和协议)
        settings_out = self.run_shell_command("warp-cli settings")
        
        # 精准解析模式
        mode_match = re.search(r"Mode:\s*(.*)", settings_out)
        self.mode = mode_match.group(1).strip() if mode_match else "Unknown"
        
        # 精准解析协议设置
        proto_match = re.search(r"WARP tunnel protocol:\s*(.*)", settings_out)
        if proto_match:
            self.protocol = proto_match.group(1).strip()
        else:
            proto_match_alt = re.search(r"Protocol:\s*(.*)", settings_out)
            self.protocol = proto_match_alt.group(1).strip() if proto_match_alt else "Unknown"

        # 更新图标和标题
        if self.icon:
            if self.status_raw == "Connected": color = "green"
            elif self.status_raw == "Connecting": color = "orange"
            else: color = "red"
            
            self.icon.icon = self.create_image(color)
            self.icon.title = f"WARP: {self.status_display}\n{self.t['mode']}: {self.mode}\n{self.t['proto']}: {self.protocol}"
            self.icon.update_menu()

    def start_short_term_monitor(self):
        """启动一个短时间的监控线程，直到状态稳定或超时"""
        def monitor():
            start_time = time.time()
            # 监控最多持续 20 秒，应对注册后的自动连接
            while time.time() - start_time < 20:
                self.update_warp_state()
                # 如果状态已经稳定（不再是 Connecting），则停止监控
                if self.status_raw != "Connecting":
                    break
                time.sleep(1)
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
            
        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()

    def create_image(self, color):
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((4, 4, 60, 60), outline="white", width=2)
        dc.ellipse((12, 12, 52, 52), fill=color)
        return image

    def on_connect(self):
        self.run_shell_command("warp-cli connect")
        self.update_warp_state()
        self.start_short_term_monitor()

    def on_disconnect(self):
        self.run_shell_command("warp-cli disconnect")
        self.update_warp_state()
        self.start_short_term_monitor()

    def on_set_protocol(self, proto):
        self.run_shell_command(f"warp-cli tunnel protocol set {proto}")
        self.update_warp_state()

    def on_reset_settings(self):
        self.run_shell_command("warp-cli settings reset")
        self.check_and_register()
        self.update_warp_state()

    def on_quit(self, icon, item):
        self.running = False
        icon.stop()
        if self.lock_file:
            try:
                fcntl.lockf(self.lock_file, fcntl.LOCK_UN)
                self.lock_file.close()
                os.remove(self.lock_file_path)
            except:
                pass
        os.killpg(os.getpgrp(), signal.SIGKILL)

    def setup_menu(self):
        return pystray.Menu(
            item(lambda text: f"{self.t['status']}: {self.status_display}", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item(self.t['connect'], self.on_connect, visible=lambda item: self.status_raw != "Connected"),
            item(self.t['disconnect'], self.on_disconnect, visible=lambda item: self.status_raw == "Connected"),
            pystray.Menu.SEPARATOR,
            item(self.t['protocol'], pystray.Menu(
                item('MASQUE', lambda: self.on_set_protocol('MASQUE'), checked=lambda item: self.protocol.upper() == "MASQUE"),
                item('WireGuard', lambda: self.on_set_protocol('WireGuard'), checked=lambda item: self.protocol.upper() == "WIREGUARD"),
            )),
            item(self.t['reset_settings'], self.on_reset_settings),
            pystray.Menu.SEPARATOR,
            item(self.t['quit'], self.on_quit)
        )

    def run(self):
        # 1. 检查单例运行
        if not self.check_single_instance():
            sys.exit(0)
            
        # 2. 启动增强的自动注册检测
        self.check_and_register()
            
        # 3. 获取初始状态
        self.update_warp_state()
        color = "green" if self.status_raw == "Connected" else ("orange" if self.status_raw == "Connecting" else "red")
        initial_title = f"WARP: {self.status_display}\n{self.t['mode']}: {self.mode}\n{self.t['proto']}: {self.protocol}"
        
        self.icon = pystray.Icon("WARP", self.create_image(color), initial_title, menu=self.setup_menu())
        
        # 如果启动时处于连接中，也开启监控
        if self.status_raw == "Connecting":
            self.start_short_term_monitor()
            
        self.icon.run()

if __name__ == "__main__":
    try:
        os.setpgrp()
    except:
        pass
    app = WarpGUI()
    app.run()
