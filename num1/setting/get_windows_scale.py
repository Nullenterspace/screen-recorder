import ctypes
from ctypes import wintypes

# 必须开启 DPI 感知，否则获取不到真实缩放
user32 = ctypes.WinDLL('user32', use_last_error=True)
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)

def get_windows_scale():
    try:
        # 获取桌面窗口
        hWnd = user32.GetDesktopWindow()
        # 获取DC
        hdc = user32.GetDC(hWnd)

        # ==================== C++ 原版逻辑 ====================
        # 1. 获取【虚拟分辨率】 SM_CXSCREEN/SM_CYSCREEN
        screenW = user32.GetSystemMetrics(0)  # 0=SM_CXSCREEN
        screenH = user32.GetSystemMetrics(1)  # 1=SM_CYSCREEN

        # 2. 获取【真实物理分辨率】 DESKTOPHORZRES / DESKTOPVERTRES
        realWidth = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)  # 118=DESKTOPHORZRES
        realHeight = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117) # 117=DESKTOPVERTRES
        # ======================================================

        # 释放资源
        user32.ReleaseDC(hWnd, hdc)

        # 计算缩放 = 物理分辨率 / 虚拟分辨率
        scale = realWidth / screenW
        print(f"虚拟分辨率: {screenW} x {screenH}")
        print(f"物理分辨率: {realWidth} x {realHeight}")
        print(f"系统缩放: {scale}")
        return scale

    except Exception as e:
        print("获取失败:", e)
        return 1.0

# 测试
SCALE = get_windows_scale()