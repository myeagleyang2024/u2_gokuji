<<<<<<< HEAD
# u2_gokuji
=======
# u2_gokuji - uiautomator2 入魂一番赏自动化工程
#
# 目录结构：
# ├── scripts/        # 业务脚本（按功能分类）
# ├── lib/            # 工具库（adb_utils, ui_utils 等）
# ├── config/         # 配置文件
# ├── output/         # 截图、xml dump 等输出
# ├── README.md       # 工程说明
# └── requirements.txt

## 前置条件

### 1. 安装 Python 依赖
```bash
# 使用 Python 3.9（MuMu 模拟器专用路径）
C:\Users\23972\AppData\Local\Programs\Python\Python39\python.exe -m pip install uiautomator2
```

### 2. 确保模拟器已连接
```bash
adb devices
# 应该看到 emulator-5554  device
```

### 3. 初始化 uiautomator2
```bash
# 首次使用需要安装 atx-agent 到模拟器
C:\Users\23972\AppData\Local\Programs\Python\Python39\python.exe -m uiautomator2 init
```

## 代码查看入口

推荐从以下文件开始阅读：

1. **入口脚本**: `scripts/daily_run.py` — 完整的自动遍历流程
2. **Tab 坐标定义**: `config/tab_config.py` — 所有 tab 定义
3. **工具库**: `lib/adb_utils.py` — ADB 工具函数
4. **工具库**: `lib/ui_utils.py` — UI 解析工具函数
5. **抓包集成**: `lib/mitm_utils.py` — 与 mitmweb 集成的工具函数

## 操作流程

标准操作流程：
1. 启动抓包（mitmweb + iptables）— 参考底部说明
2. 运行 `python scripts/daily_run.py`
3. 查看 `output/` 下的截图和 XML
4. 查看 `../data/raw/` 下的 API 响应

## Tab 布局（已确认）

```
底部导航栏（y≈1540）：
+--------+--------+--------+--------+
|  首页   | (空)   |  赏柜   |  我的   |
| x=150  | x=300  | x=600  | x=750  |
+--------+--------+--------+--------+
         (旧赏柜坐标，无箱子)
```

> ⚠️ 注意：赏柜 tab 的准确坐标是 x=600, y=1540（不是之前的 x=450, y=1520）

## 抓包代理

抓包需要先启动代理：

### 启动 mitmweb
```bash
# 终端1: 启动 mitmweb
start_mitmweb.bat
```

### 配置 iptables
```bash
adb shell "su -c 'iptables -t nat -F OUTPUT; iptables -t nat -A OUTPUT -p tcp --dport 80 -j REDIRECT --to-port 8082; iptables -t nat -A OUTPUT -p tcp --dport 443 -j REDIRECT --to-port 8082'"
adb reverse tcp:8082 tcp:8082
```

### 验证
```bash
curl -x 127.0.0.1:8082 https://wechatapp.ichibankuji.cn -k
```

## 同时运行监控（可选）
```bash
# 终端2: 监控 API 响应
# 查看 data/raw/ 目录下的 *.txt 文件
```
>>>>>>> origin/u2-0000
