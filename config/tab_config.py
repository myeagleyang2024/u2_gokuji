# 入魂一番赏 - uiautomator2 自动化配置

# ===== Tab 布局（底部导航栏 y≈1540） =====
# 经验证，底部共 3 个 tab：
# 首页(112) | 赏柜(450) | 我的(787)
TABS = {
    "home": {"label": "首页", "x": 112, "y": 1540},
    "box":  {"label": "赏柜", "x": 450, "y": 1540},
    "mine": {"label": "我的", "x": 787, "y": 1540},
}

# ===== App 信息 =====
APK_NAME = "入魂一番赏_4.2.21_APKPure.apk"
PACKAGE_NAME = "com.allyes.gokuji"

# ===== 设备配置 =====
DEVICE_SERIAL = "emulator-5554"
ADB_PATH = r"C:\lars\android-sdk-2\platform-tools\adb.exe"
SCREEN_SIZE = (900, 1600)

# ===== 入魂赏入口（需要确认） =====
# 入魂赏入口在首页内容区，具体坐标待确认
# 首页中部标签: 今日推荐(x=130,y=666), 新品预约(x=313,y=666), 折扣专区(x=497,y=666)

# ===== 代理配置 =====
PROXY_PORT = 8082
MITM_WEB_PORT = 8081

# ===== 输出目录 =====
OUTPUT_DIR = "output"
RAW_DATA_DIR = "../data/raw"
