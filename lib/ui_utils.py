# -*- coding: utf-8 -*-
"""
UI 元素解析工具函数

基于 uiautomator2 dump_hierarchy 返回的 XML 解析。
入魂一番赏 是 Flutter 应用，大部分 UI 在 Android accessibility tree 中
以 content-desc 显示，text 属性很少。
"""
import re
from typing import List, Dict, Optional, Tuple


def parse_xml_nodes(xml: str) -> List[Dict]:
    """
    从 XML dump 中解析所有 node
    
    返回每个 node 的字典:
    - x1, y1, x2, y2: bounds
    - cx, cy: 中心坐标
    - w, h: 宽高
    - text: text 属性（Flutter 中很少）
    - desc: content-desc（Flutter 的主要内容）
    - clickable: 是否可点击
    """
    nodes = []
    pattern = r'<node[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?>'
    
    for m in re.finditer(pattern, xml):
        x1, y1, x2, y2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        text_m = re.search(r'text="([^"]*)"', m.group(0))
        desc_m = re.search(r'content-desc="([^"]*)"', m.group(0))
        rid_m = re.search(r'resource-id="([^"]*)"', m.group(0))
        
        text = text_m.group(1) if text_m else ""
        desc = desc_m.group(1) if desc_m else ""
        rid = rid_m.group(1) if rid_m else ""
        clk = "clickable" in m.group(0)
        
        nodes.append({
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "cx": (x1 + x2) // 2, "cy": (y1 + y2) // 2,
            "w": x2 - x1, "h": y2 - y1,
            "text": text, "desc": desc, "rid": rid,
            "clickable": clk,
        })
    return nodes


def find_boxes(nodes: List[Dict],
               width_range=(150, 500),
               height_range=(100, 600),
               y_range=(200, 1400),
               min_desc_len: int = 5) -> List[Dict]:
    """
    从 node 列表中筛选出"箱子"卡片
    
    特征:
    - 中等大小（不是 tab 按钮也不是全屏元素）
    - 在内容区 y 范围内
    - 有足够的 desc 内容（Flutter 卡片）
    """
    candidates = [n for n in nodes
                  if width_range[0] <= n["w"] <= width_range[1]
                  and height_range[0] <= n["h"] <= height_range[1]
                  and y_range[0] <= n["cy"] <= y_range[1]
                  and len(n["desc"]) >= min_desc_len]
    return candidates


def dedup_nodes(nodes: List[Dict], min_distance: int = 50) -> List[Dict]:
    """
    按位置去重（相同位置的节点只保留第一个）
    先按 y 排序，再按 x 排序
    """
    if not nodes:
        return []
    
    sorted_nodes = sorted(nodes, key=lambda n: (n["y1"], n["x1"]))
    dedup = [sorted_nodes[0]]
    for b in sorted_nodes[1:]:
        last = dedup[-1]
        if abs(b["cx"] - last["cx"]) > min_distance or abs(b["cy"] - last["cy"]) > min_distance:
            dedup.append(b)
    return dedup


def find_tab_items(nodes: List[Dict],
                   y_range=(1500, 1600),
                   x_range=(0, 900),
                   min_size: int = 20) -> List[Dict]:
    """
    找底部导航栏 tab 按钮
    """
    return [n for n in nodes
            if y_range[0] <= n["cy"] <= y_range[1]
            and x_range[0] <= n["cx"] <= x_range[1]
            and n["w"] >= min_size and n["h"] >= min_size]


def safe_desc(node: Dict, maxlen: int = 40) -> str:
    """安全打印 desc（处理 Unicode 编码问题）"""
    return node["desc"][:maxlen].encode("ascii", errors="replace").decode("ascii")


def print_nodes(nodes: List[Dict], max_count: int = 10):
    """打印节点摘要"""
    for i, n in enumerate(nodes[:max_count]):
        print(f"  [{n['x1']},{n['y1']}][{n['x2']},{n['y2']}] "
              f"{n['w']}x{n['h']} clk={n['clickable']} "
              f"desc={safe_desc(n)}")
