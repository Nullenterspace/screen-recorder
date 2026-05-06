import pyautogui
import csv
import json
import time
import os

# ===================== 路径配置 =====================
SAVE_FOLDER = "save"
PARAM_FOLDER = "param"
config_path = os.path.join(PARAM_FOLDER, "frame_config.json")

# 读取帧间隔
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
frame_interval = config["frame_interval"]

# ===================== 读取录制数据 =====================
data = []
with open(os.path.join(SAVE_FOLDER, "mouse_movement.csv"), "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        x = float(row[0])
        y = float(row[1])
        left = int(row[2])
        right = int(row[3])
        scroll = int(row[4])
        data.append([x, y, left, right, scroll])

# ===================== 开始回放 =====================
print("开始回放鼠标，共 %d 帧" % len(data))
time.sleep(1)

last_left = 0
last_right = 0

for x, y, left, right, scroll in data:
    pyautogui.moveTo(x, y, _pause=False)

    # 左键
    if left != last_left:
        if left == 1:
            pyautogui.mouseDown(button="left", _pause=False)
        else:
            pyautogui.mouseUp(button="left", _pause=False)
        last_left = left

    # 右键
    if right != last_right:
        if right == 1:
            pyautogui.mouseDown(button="right", _pause=False)
        else:
            pyautogui.mouseUp(button="right", _pause=False)
        last_right = right

    # 滚轮
    if scroll != 0:
        pyautogui.scroll(scroll, _pause=False)

    time.sleep(frame_interval)

print(" 回放完成！")