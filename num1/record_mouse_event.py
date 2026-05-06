from pynput import mouse
import keyboard
import csv
import time
import os
import json

# ===================== 配置 =====================
# 检测文件夹
if not os.path.exists("save"):
    os.makedirs("save")

# 从 JSON 读取帧间隔（你可以自己改 json 内容）
with open("param/frame_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
frame_interval = config["frame_interval"]  # 帧间隔（秒）

# ===================== 鼠标状态 =====================
current_x = 0
current_y = 0
left_state = 0  # 0=松开 1=按住
right_state = 0
scroll_state = 0  # +1上滚 -1下滚 0无
last_scroll_time = 0

mouse_movement = []
start_time = time.time()


# ===================== 监听函数 =====================
def on_move(x, y):
    global current_x, current_y
    current_x = x
    current_y = y


def on_click(x, y, button, pressed):
    global left_state, right_state
    if button == mouse.Button.left:
        left_state = 1 if pressed else 0
    if button == mouse.Button.right:
        right_state = 1 if pressed else 0


def on_scroll(x, y, dx, dy):
    global scroll_state, last_scroll_time
    scroll_state = dy
    last_scroll_time = time.time()  # 每次滚动都更新时间
    print('Scrolled at ({0}, {1}) with {2} and {3}'.format(x, y, dx, dy))


def reset_scroll_when_idle():
    global scroll_state
    # 如果超过 0.05 秒没滚动，就设为0（停止）
    if time.time() - last_scroll_time > 0.1 and scroll_state != 0:
        print("stop:", time.time())
        scroll_state = 0


# ===================== 启动监听 =====================
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll
)
listener.start()

print(" 开始录制鼠标，按 F1 停止")
print(f" 帧间隔：{frame_interval}s")

# ===================== 主循环 =====================
while True:
    reset_scroll_when_idle()
    if keyboard.is_pressed("f1"):
        print(" 停止录制")
        break

    # 按你要求的结构：x, y, 左键, 右键, 滚轮
    mouse_movement.append([
        current_x,
        current_y,
        left_state,
        right_state,
        scroll_state
    ])
    # scroll_state = 0  # 滚轮只触发一帧
    time.sleep(frame_interval)

listener.stop()

# ===================== 写入CSV（完全按你的写法） =====================
with open('save/mouse_movement.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    print(len(mouse_movement))
    for event in mouse_movement:
        # print(event)
        if event[0] != 0 or event[1] != 0:
            csv_writer.writerow(event)

print(" 保存完成：save/mouse_movement.csv")
