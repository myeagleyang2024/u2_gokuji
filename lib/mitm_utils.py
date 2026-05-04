# -*- coding: utf-8 -*-
"""
mitmproxy 抓包集成工具函数
"""
import os
import subprocess
import re
from typing import Optional, List


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")


def check_mitmweb_running(port: int = 8081) -> bool:
    """检查 mitmweb 是否在运行"""
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3)
        return True
    except:
        return False


def check_proxy(port: int = 8082) -> bool:
    """验证代理转发是否正常"""
    import urllib.request
    proxy_handler = urllib.request.ProxyHandler({"http": f"http://127.0.0.1:{port}",
                                                  "https": f"http://127.0.0.1:{port}"})
    opener = urllib.request.build_opener(proxy_handler)
    try:
        r = opener.open("http://wechatapp.ichibankuji.cn", timeout=5)
        return r.status == 200
    except:
        return False


def get_captured_apis(prefix: str = "") -> List[str]:
    """返回已捕获的 API 文件列表"""
    if not os.path.exists(DATA_DIR):
        return []
    files = [f for f in os.listdir(DATA_DIR)
             if f.startswith("res_") and prefix in f]
    return sorted(files)


def get_box_details() -> List[dict]:
    """获取已捕获的 boxDetail 数据"""
    files = get_captured_apis("boxDetail")
    results = []
    for f in files:
        path = os.path.join(DATA_DIR, f)
        size = os.path.getsize(path)
        # 提取时间戳
        m = re.match(r"res_(\d+)_", f)
        ts = m.group(1) if m else "???"
        results.append({"file": f, "size": size, "timestamp": ts})
    return results
