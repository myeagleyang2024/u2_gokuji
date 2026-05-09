# -*- coding: utf-8 -*-
"""
入魂一番赏 API 通用请求客户端

请求格式（加密）:
  body = {"da": "<base64>!<base64>"}

请求头固定字段:
  user-agent: Dart/3.10 (dart:io)
  version: 4.3.6
  channel: ichibankuji
  terminalos: android
  content-type: application/json
  authorization: 每次请求动态生成（! 分隔格式）

用法:
  from lib.api_client import GokujiAPI

  api = GokujiAPI()
  # 直发 da 密文
  data = api.request_da("/wechat/yfs/getTabList", {
      "da": "IqHj+ftnFz2XDnbhAThvmE...="
  })

  # 或直接调用快捷方法（已预填最新 da 值，但可能过期）
  data = api.get_tab_list()
"""
import json
import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("gokuji_api")

# ============================================================
# 常量
# ============================================================
BASE_URL = "https://wechatapp.ichibankuji.cn"
USER_AGENT = "Dart/3.10 (dart:io)"
VERSION = "4.3.6"
CHANNEL = "ichibankuji"
TERMINAL_OS = "android"


# ============================================================
# 配置
# ============================================================
@dataclass
class GokujiAPIConfig:
    """API 客户端配置"""
    base_url: str = BASE_URL
    user_agent: str = USER_AGENT
    version: str = VERSION
    channel: str = CHANNEL
    terminal_os: str = TERMINAL_OS
    authorization: str = "0e019LhcmtSvMa!2BtwtCbW8cN0!1QgbjQhPhOUImeFSApMzxj8kxeKSHFygrIn7!2jhUpW6ZABZhOfLrvQ9q3VmkeblKrTaWWpI5Sj0yXsADIInJrw="  # 环境变量 GOKUJI_AUTH 优先
    timeout: int = 15
    proxy: Optional[Dict[str, str]] = None  # 如 {"http": "http://127.0.0.1:8082"}


# ============================================================
# 辅助函数
# ============================================================

def _get_authorization() -> str:
    """从环境变量或默认值获取 authorization"""
    env = os.environ.get("GOKUJI_AUTH")
    if env:
        return env
    return "0e019LhcmtSvMa!2BtwtCbW8cN0!1QgbjQhPhOUImeFSApMzxj8kxeKSHFygrIn7!2jhUpW6ZABZhOfLrvQ9q3VmkeblKrTaWWpI5Sj0yXsADIInJrw="


# ============================================================
# 主 API 客户端
# ============================================================

class GokujiAPI:
    """入魂一番赏 API 客户端"""

    def __init__(self, config: Optional[GokujiAPIConfig] = None):
        self.config = config or GokujiAPIConfig()

    # --------------------------------------------------
    # 核心请求方法
    # --------------------------------------------------

    def request_da(self, path: str, body: dict,
                   method: str = "POST") -> Optional[Dict[str, Any]]:
        """
        发送 da 密文请求（与 App 行为一致）

        body 应包含 "da" 字段，值为从 App 抓取的密文。
        也可以传明文 JSON（如果服务器接受明文，如 protocolVersion/get），
        但大部分 API 需要加密 da 字段。

        Args:
            path: API 路径，如 "/wechat/yfs/getTabList"
            body: 请求体字典（{"da": "..."} 或 {}）
            method: HTTP 方法

        Returns:
            解析后的 JSON 响应
        """
        url = self.config.base_url.rstrip("/") + "/" + path.lstrip("/")

        headers = {
            "user-agent": self.config.user_agent,
            "version": self.config.version,
            "channel": self.config.channel,
            "terminalos": self.config.terminal_os,
            "content-type": "application/json",
            "accept-encoding": "gzip",
            "authorization": _get_authorization(),
        }

        logger.debug(f"请求: {method} {url}")

        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                timeout=self.config.timeout,
                proxies=self.config.proxy,
                verify=False,
            )
            logger.debug(f"响应: {resp.status_code} ({len(resp.content)} bytes)")
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"响应非 JSON: {e} -> {resp.text[:200]}")
            return {"_raw": resp.text}

    # --------------------------------------------------
    # 快捷方法
    # --------------------------------------------------

    def get_tab_list(self, da: str = "") -> Optional[Dict]:
        """获取首页 Tab 列表"""
        body = {}
        if da:
            body["da"] = da
        return self.request_da("/wechat/yfs/getTabList", body)

    def get_home_list(self, page: int = 1, page_size: int = 20,
                      da: str = "") -> Optional[Dict]:
        """获取首页商品列表"""
        body = {"pageNum": page, "pageSize": page_size}
        if da:
            body["da"] = da
        return self.request_da("/wechat/yfs/getHomeList", body)

    def get_banners(self, da: str = "") -> Optional[Dict]:
        """获取首页 Banner"""
        body = {}
        if da:
            body["da"] = da
        return self.request_da("/wechat/yfs/getBanners", body)

    def get_user_info(self, da: str = "") -> Optional[Dict]:
        """获取用户信息"""
        body = {}
        if da:
            body["da"] = da
        return self.request_da("/wechat/mini/getUserInfo", body)

    def get_box_detail(self, box_id: str, da: str = "") -> Optional[Dict]:
        """获取赏箱详情"""
        body = {"boxId": box_id}
        if da:
            body["da"] = da
        return self.request_da("/wechat/yfs/boxDetail", body)

    def get_irhunshang_list(self, tab_id: str = "", page: int = 1,
                            page_size: int = 10, da: str = "") -> Optional[Dict]:
        """获取入魂赏商品列表"""
        body = {"tabId": tab_id, "pageNum": page, "pageSize": page_size}
        if da:
            body["da"] = da
        return self.request_da("/wechat/yfs/irhunshang/getIrHunShangPageList", body)

    # --------------------------------------------------
    # 从 mitm 流量文件中提取最新 da 值
    # --------------------------------------------------

    @staticmethod
    def extract_latest_da(mitm_path: str = None,
                          api_path: str = "/wechat/yfs/getTabList") -> Optional[str]:
        """
        从 mitmproxy 保存的 .mitm 流量文件中提取指定 API 的最新 da 值

        Args:
            mitm_path: .mitm 文件路径（默认自动查找 workspace 下的）
            api_path: API 路径，用于匹配

        Returns:
            da 值字符串，如果找不到返回 None
        """
        if mitm_path is None:
            # 自动查找 workspace 下的 .mitm 文件
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidates = [os.path.join(base, f) for f in os.listdir(base)
                          if f.endswith(".mitm")]
            if not candidates:
                return None
            mitm_path = max(candidates, key=os.path.getmtime)

        if not os.path.exists(mitm_path):
            logger.warning(f"mitm 文件不存在: {mitm_path}")
            return None

        try:
            from mitmproxy import io
            reader = io.FlowReader(open(mitm_path, "rb"))
            latest_da = None
            for f in reader.stream():
                if (hasattr(f, "request")
                        and api_path in f.request.path
                        and f.request.method == "POST"):
                    try:
                        body = json.loads(f.request.get_text() or "{}")
                        if "da" in body:
                            latest_da = body["da"]
                    except (json.JSONDecodeError, AttributeError):
                        continue
            return latest_da
        except Exception as e:
            logger.warning(f"读取 mitm 文件失败: {e}")
            return None


# ============================================================
# 快捷函数
# ============================================================

def quick_request(path: str, body: Optional[dict] = None,
                  proxy: bool = True) -> Optional[Dict]:
    """
    快速发起请求（一行调用）

    Args:
        path: API 路径
        body: 请求体（包含 da 或 明文）
        proxy: 是否通过抓包代理

    Example:
        >>> quick_request("/wechat/yfs/getTabList", {"da": "..."})
        >>> quick_request("/wechat/yfs/boxDetail", {"boxId": "xxx"}, proxy=False)
    """
    cfg = GokujiAPIConfig()
    if proxy:
        cfg.proxy = {"http": "http://127.0.0.1:8082", "https": "http://127.0.0.1:8082"}
    api = GokujiAPI(cfg)
    return api.request_da(path, body or {})


# ============================================================
# 示例（可以直接运行）
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    api = GokujiAPI(GokujiAPIConfig())  # ← 不设代理，直接发请求

    # 自动从 mitm 流量文件中提取最新 da 值
    # 在 workspace 根目录查找最新的 .mitm 文件
    workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mitm_path = os.path.join(workspace, "flows_gokuji.mitm")
    latest_da = GokujiAPI.extract_latest_da(mitm_path, "/wechat/yfs/getTabList")
    print("latest_da: " + latest_da)
    if latest_da:
        print(f"Got da from mitm file ({len(latest_da)} chars)")
        print("=== getTabList (with da) ===")
        result = api.get_tab_list(da=latest_da)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
        else:
            print("Request failed")
    else:
        print("No da found in mitm file. Run App first.")

    print("\n=== getTabList (plaintext - expect 1010) ===")
    result2 = api.get_tab_list()
    if result2:
        print(json.dumps(result2, ensure_ascii=False, indent=2)[:500])
