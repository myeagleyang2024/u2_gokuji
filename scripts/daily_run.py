# -*- coding: utf-8 -*-
"""
每日自动遍历脚本 - 入魂一番赏

操作流程:
1. 启动 App
2. 首页截图
3. 点击"入魂赏"链接（首页中部 y≈1100）-> 进入入魂赏商品列表
4. 滑动浏览商品卡片 -> 点击商品进入详情
5. 返回首页

用法:
  python scripts/daily_run.py

入口坐标:
  - 入魂赏 link: ~(165, 1100)  首页中部 "入魂赏" 标题
  - 更多> link: ~(800, 1100)   右侧 "更多>" 按钮
  - 入魂赏页面顶部分类tags: y≈202 水平排列
"""
import sys
import os
import time
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uiautomator2 as u2
from config.tab_config import TABS, PACKAGE_NAME, OUTPUT_DIR
from lib.adb_utils import tap, swipe, keyevent, screenshot


def log(msg: str):
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] {msg}", flush=True)


def save_state(d: u2.Device, prefix: str):
    """截图 + XML dump"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img = d.screenshot(os.path.join(OUTPUT_DIR, f"{prefix}.png"))
    xml = d.dump_hierarchy()
    with open(os.path.join(OUTPUT_DIR, f"{prefix}.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    log(f"Saved: {prefix} ({len(xml)} chars)")
    return xml


def click_tab(d: u2.Device, tab_name: str):
    tab = TABS[tab_name]
    tap(tab["x"], tab["y"])
    time.sleep(4)
    save_state(d, f"tab_{tab_name}")


def enter_irhunshang(d: u2.Device):
    """从首页点击「入魂赏」链接，进入入魂赏商品列表"""
    log("=== 进入入魂赏 ===")
    
    # 入魂赏标题位置: 首页中部 y≈1063-1138, x≈41-288
    irhunshang_link_cx = 165
    irhunshang_link_cy = 1100
    
    tap(irhunshang_link_cx, irhunshang_link_cy)
    time.sleep(5)
    
    xml = save_state(d, "irhunshang_list")
    
    # 确认页面已加载（检测是否有分类标签）
    category_count = len(re.findall(r'\u7b2c\d+/\d+ \u8d5a', xml))  # "第X/12 赞"
    log(f"入魂赏页面: 分类tab数 ≈ {category_count}")
    
    return xml


def scroll_and_capture(d: u2.Device, scroll_count: int = 3):
    """在入魂赏页面滚动浏览，截图商品"""
    log(f"=== 滚动浏览 ({scroll_count}次) ===")
    
    for i in range(scroll_count):
        # 向下滚动
        swipe(450, 1200, 450, 400, 400)
        time.sleep(3)
        xml = save_state(d, f"irhunshang_scroll_{i}")
        
        # 解析商品卡片
        cards = []
        for m in re.finditer(r'<node[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?clickable="true"[^>]*?>', xml):
            x1, y1, x2, y2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            w, h = x2 - x1, y2 - y1
            if 80 <= w <= 400 and 80 <= h <= 400 and y1 > 200:
                desc_m = re.search(r'content-desc="([^"]*)"', m.group(0))
                desc = desc_m.group(1) if desc_m else ""
                cards.append({"bounds": f"[{x1},{y1}][{x2},{y2}]", "cx": (x1+x2)//2, "cy": (y1+y2)//2, "desc": desc[:60]})
        
        if cards:
            log(f"第{i+1}屏: {len(cards)} 个可点击商品")
            for c in cards[:5]:
                log(f"  {c['bounds']} desc={c['desc']}")


def run():
    log("=== 入魂一番赏 日常遍历 ===")
    
    d = u2.connect("emulator-5554")
    d.app_stop(PACKAGE_NAME)
    time.sleep(1)
    d.app_start(PACKAGE_NAME)
    time.sleep(10)
    log(f"App started")
    
    # 1. 首页截图
    save_state(d, "home")
    
    # 2. 进入入魂赏商品列表
    enter_irhunshang(d)
    
    # 3. 滚动浏览商品
    scroll_and_capture(d, scroll_count=2)
    
    # 4. 返回首页
    keyevent("BACK")
    time.sleep(3)
    click_tab(d, "home")
    
    d.app_stop(PACKAGE_NAME)
    log("=== DONE ===")


if __name__ == "__main__":
    run()
