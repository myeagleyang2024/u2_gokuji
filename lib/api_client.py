# -*- coding: utf-8 -*-
"""
入魂一番赏 API 通用请求客户端

请求格式:
  {
    "da": "<RSA加密的AES密钥(base64)>!<AES加密的JSON数据(base64)>"
  }

请求头固定字段:
  authorization: 每次请求动态生成（! 分隔格式）
  user-agent: Dart/3.10 (dart:io)
  version: 4.3.6
  channel: ichibankuji
  terminalos: android
  content-type: application/json

响应格式:
  大部分为明文 JSON（可直接解析）
  少部分也可能加密（待确认）

用法:
  from lib.api_client import GokujiAPI

  api = GokujiAPI()
  # 不加密原始请求（如果App能收到明文响应）
  data = api.request("/wechat/yfs/getTabList", {})

  # 或加密请求（模拟App行为）
  data = api.request_encrypted("/wechat/yfs/getTabList", {"some": "data"})
"""
import json
import os
import time
import hashlib
import base64
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

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
    uid: str = "200742579"
    token: str = ""  # authorization token（抓包获取或自动生成）
    encrypt: bool = False  # 默认不加密（响应明文，直接发 JSON）
    timeout: int = 15
    proxy: Optional[Dict[str, str]] = None  # 如 {"http": "http://127.0.0.1:8082", "https": "http://127.0.0.1:8082"}
    # 加密相关（待逆向 libapp.so 后填写）
    rsa_public_key: Optional[str] = None  # PEM 格式
    aes_key: Optional[bytes] = None       # 16/24/32 bytes


# ============================================================
# 辅助函数
# ============================================================

def _make_authorization(uid: str, token: str = "") -> str:
    """
    生成 authorization 请求头

    从抓包看格式为: "<base64>!<base64>"
    可能包含 uid/token/sign 等信息。目前先返回固定值，
    后续逆向 libapp.so 后实现真实签名。
    """
    if token:
        return token
    # 临时占位（从抓包复制一个可用的 token）
    return "0e019LhcmtSvMa!2BtwtCbW8cN0!1QgbjQhPhOUImeFSApMzxj8kxeKSHFygrIn7!2jhUpW6ZABZhOfLrvQ9q3VmkeblKrTaWWpI5Sj0yXsADIInJrw="


def _make_sign(data: Dict) -> str:
    """
    生成 sign 签名（如有需要）

    从之前抓包看，protocolVersion/get 有 sign 参数，
    其他请求暂时未发现必须的签名逻辑，后续补齐。
    """
    # TODO: 逆向 libapp.so 后实现真实签名算法
    return ""


def _pack_da(aes_key: bytes, plaintext: bytes) -> str:
    """
    包装 da 字段: RSA(AES密钥)!AES(JSON数据)

    Args:
        aes_key: 随机生成的 AES 密钥 (16/24/32 bytes)
        plaintext: 要加密的 JSON 字节串

    Returns:
        "<RSA加密的AES密钥(base64)>!<AES加密的数据(base64)>"
    """
    # TODO: 实现 RSA 加密 AES 密钥 + AES-CBC/PKCS7 加密数据
    # 需要 libapp.so 逆向出 RSA 公钥和 AES 模式
    raise NotImplementedError("加密功能需要逆向 libapp.so 后实现")


# ============================================================
# 主 API 客户端
# ============================================================

class GokujiAPI:
    """入魂一番赏 API 客户端"""

    def __init__(self, config: Optional[GokujiAPIConfig] = None):
        self.config = config or GokujiAPIConfig()
        self._session = requests.Session()
        self._session.headers.update(self._default_headers())

    def _default_headers(self) -> Dict[str, str]:
        return {
            "user-agent": self.config.user_agent,
            "version": self.config.version,
            "channel": self.config.channel,
            "terminalos": self.config.terminal_os,
            "content-type": "application/json",
            "accept-encoding": "gzip",
        }

    def _refresh_auth(self):
        """刷新 authorization 头（每次请求前调用）"""
        self._session.headers["authorization"] = _make_authorization(
            self.config.uid, self.config.token
        )

    # --------------------------------------------------
    # 请求方法
    # --------------------------------------------------

    def request(self, path: str, data: Optional[Dict] = None,
                method: str = "POST") -> Optional[Dict[str, Any]]:
        """
        发送明文 JSON 请求（适用于响应为明文的 API）

        Args:
            path: API 路径，如 "/wechat/yfs/getTabList"
            data: JSON 数据（直接作为 body 发送）
            method: HTTP 方法，默认 POST

        Returns:
            解析后的 JSON 响应，或 None（失败时）
        """
        url = self.config.base_url.rstrip("/") + "/" + path.lstrip("/")
        self._refresh_auth()

        payload = data if data is not None else {}
        logger.debug(f"请求: {method} {url}")

        try:
            resp = self._session.request(
                method=method,
                url=url,
                json=payload,
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

    def request_encrypted(self, path: str, data: Optional[Dict] = None,
                          method: str = "POST") -> Optional[Dict[str, Any]]:
        """
        发送加密请求（模拟 App 行为，body 为 {"da": "..."}）

        需要先配置 RSA 公钥和 AES 密钥。
        未配置时会抛出 NotImplementedError。

        Args:
            path: API 路径
            data: 要加密的 JSON 数据
            method: HTTP 方法

        Returns:
            解析后的 JSON 响应
        """
        # 检查是否配置了 RSA 公钥，如果没有则抛出 NotImplementedError
        if not self.config.rsa_public_key:
            raise NotImplementedError(
                "请先配置 rsa_public_key，或使用 request() 方法发送明文"
            )

        # 构建完整的 URL，确保 base_url 和 path 之间的斜杠正确
        url = self.config.base_url.rstrip("/") + "/" + path.lstrip("/")
        # 刷新认证信息
        self._refresh_auth()

        # 生成随机 AES 密钥
        import os
        aes_key = self.config.aes_key or os.urandom(32)

        # 包装 da 字段
        payload_json = json.dumps(data or {}, ensure_ascii=False).encode("utf-8")
        da = _pack_da(aes_key, payload_json)

        logger.debug(f"加密请求: {method} {url}")
        try:
            resp = self._session.request(
                method=method,
                url=url,
                json={"da": da},
                timeout=self.config.timeout,
                proxies=self.config.proxy,
            )
            logger.debug(f"响应: {resp.status_code} ({len(resp.content)} bytes)")
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None
        except json.JSONDecodeError:
            logger.warning(f"响应非 JSON: {resp.text[:200]}")
            return {"_raw": resp.text}

    # --------------------------------------------------
    # 快捷方法：常用 API
    # --------------------------------------------------

    def get_tab_list(self) -> Optional[Dict]:
        """获取首页 Tab 列表"""
        data = {
            "da": "Q5pGDxOLo/PSdKzNFicSb8BlkOhZHumbP6dlrCQihedYCG9/+X0Va2GoHj5Mh0htzz0w7bQXOIHr2nHlQS/vV6AWQuIkLzaXwZtz6lj2HodoOo6TEOV9HkCWy5rO+kZj5cJi2qMFbOvIKiIl2oFcMSWL+t/AHw1rW91g5wVQ5oGKXSFrnAXQn4vwanzQ+jVpmX!gWmVEHF6YkS3ynwlD1AuducCvhCaQ7yXgrfq1acr4yOjaE8CI6i06LiEHvB3cUzudQU/wjSHXd1wH15QkJcojXChpLCzvj+e8gmHMeJUUvNMI3C3aSCJp6qIglsGKIuWoAfaJBCy0Gf2oUMk2AgvCbGdN0p6flHMy3ieWtYJadkos="
        }
        return self.request("/wechat/yfs/getTabList", {})

    def get_home_list(self, page: int = 1, page_size: int = 20) -> Optional[Dict]:
        """获取首页商品列表"""
        data = {"pageNum": page, "pageSize": page_size}
        return self.request("/wechat/yfs/getHomeList", data)

    def get_banners(self) -> Optional[Dict]:
        """获取首页 Banner"""
        return self.request("/wechat/yfs/getBanners", {})

    def get_user_info(self) -> Optional[Dict]:
        """获取用户信息"""
        return self.request("/wechat/yfs/getUserInfo", {})

    def get_box_detail(self, box_id: str) -> Optional[Dict]:
        """获取赏箱详情"""
        return self.request("/wechat/yfs/boxDetail", {"boxId": box_id})

    def get_irhunshang_list(self, tab_id: str = "", page: int = 1,
                            page_size: int = 10) -> Optional[Dict]:
        """获取入魂赏商品列表"""
        data = {
            "tabId": tab_id,
            "pageNum": page,
            "pageSize": page_size,
        }
        return self.request("/wechat/yfs/irhunshang/getIrHunShangPageList", data)


# ============================================================
# 简易用法（直接调用）
# ============================================================

def quick_request(path: str, data: Optional[Dict] = None,
                  proxy: bool = True) -> Optional[Dict]:
    """
    快速发起请求（一行调用）

    Args:
        path: API 路径
        data: JSON 数据
        proxy: 是否通过抓包代理（默认 True，走 127.0.0.1:8082）

    Example:
        >>> from lib.api_client import quick_request
        >>> quick_request("/wechat/yfs/getTabList", {})
        >>> quick_request("/wechat/yfs/boxDetail", {"boxId": "xxx"}, proxy=False)
    """
    cfg = GokujiAPIConfig()
    if proxy:
        cfg.proxy = {"http": "http://127.0.0.1:8082", "https": "http://127.0.0.1:8082"}
    api = GokujiAPI(cfg)
    return api.request(path, data)


# ============================================================
# 示例
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

    # 用法 1: 通过代理（抓包）
    api = GokujiAPI(GokujiAPIConfig(
        proxy={"http": "http://127.0.0.1:8082", "https": "http://127.0.0.1:8082"}
    ))

    print("=== getTabList ===")
    result = api.get_tab_list()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
    else:
        print("请求失败")

    # 用法 2: 直接请求（不走代理）
    # result = quick_request("/wechat/yfs/getBanners", {}, proxy=False)
