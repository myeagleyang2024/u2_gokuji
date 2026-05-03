# -*- coding: utf-8 -*-
"""
uiautomator2 ADB 工具函数集合
"""
import subprocess
import time
from typing import Tuple, Optional

# 默认 ADB 路径
ADB_PATH = r"C:\lars\android-sdk-2\platform-tools\adb.exe"
DEVICE = "emulator-5554"


def adb(*args: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """执行 adb 命令"""
    cmd = [ADB_PATH, "-s", DEVICE] + list(args)
    return subprocess.run(cmd, capture_output=True, timeout=timeout)


def tap(x: int, y: int) -> bool:
    """用 adb shell input tap 模拟点击"""
    r = adb("shell", "input", "tap", str(x), str(y), timeout=5)
    return r.returncode == 0


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300):
    """滑动"""
    adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms))


def keyevent(key: str):
    """发送按键事件"""
    adb("shell", "input", "keyevent", key)


def screenshot(path: str):
    """截屏保存到本地路径"""
    # 先截到设备临时目录
    adb("shell", "screencap", "-p", "/data/local/tmp/screen.png")
    # 拉到本地
    adb("pull", "/data/local/tmp/screen.png", path)


def get_installed_packages() -> list:
    """列出已安装的应用包名"""
    r = adb("shell", "pm", "list", "packages", timeout=10)
    return [line.replace("package:", "").strip()
            for line in r.stdout.decode("utf-8", errors="replace").splitlines()]


def install_apk(apk_path: str) -> bool:
    """安装 APK"""
    r = adb("install", "-r", apk_path, timeout=120)
    return "Success" in r.stdout.decode("utf-8", errors="replace")


def setup_iptables():
    """配置 iptables REDIRECT 将 80/443 流量劫持到 mitmproxy (8082)"""
    cmd = ("su -c 'iptables -t nat -F OUTPUT; "
           "iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8082; "
           "iptables -t nat -A OUTPUT -p tcp --dport 443 -j REDIRECT --to-port 8082'")
    r = adb("shell", cmd, timeout=10)
    if r.returncode != 0:
        # 尝试不带 su -c (模拟器已 root)
        r = adb("shell", "iptables", "-t", "nat", "-F", "OUTPUT", timeout=5)
        adb("shell", "iptables", "-t", "nat", "-A", "OUTPUT",
            "-p", "tcp", "--dport", "80", "-j", "REDIRECT", "--to-port", "8082")
        adb("shell", "iptables", "-t", "nat", "-A", "OUTPUT",
            "-p", "tcp", "--dport", "443", "-j", "REDIRECT", "--to-port", "8082")


def clear_iptables():
    """清理 iptables 规则"""
    cmd = "su -c 'iptables -t nat -F OUTPUT'"
    adb("shell", cmd, timeout=5)


def setup_adb_reverse():
    """设置 adb reverse 转发"""
    adb("reverse", "tcp:8082", "tcp:8082")
