from pynput import mouse
import keyboard
import csv
import time

# 创建一个空列表用于存储鼠标事件
mouse_events = []
time_start = time.time()


def on_click(x, y, button, pressed):
    current_time = time.time()
    action = 'click' if pressed else 'release'
    mouse_events.append([action, button.name, current_time - time_start])  # 存 button.name 更清晰


def on_scroll(x, y, dx, dy):
    current_time = time.time()
    if mouse_events:
        if mouse_events[-1][0] == "scroll" and dy == mouse_events[-1][1]:
            mouse_events[-1][2][-1] = current_time - time_start
        else:
            mouse_events.append(['scroll', dy, [current_time - time_start, current_time - time_start]])
    else:
        mouse_events.append(['scroll', dy, [current_time - time_start, current_time - time_start]])


# 创建并启动鼠标监听器
listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
listener.start()
print("已开始记录鼠标事件，按 F1 停止并保存")

# ---------------- 关键修复：等待 F1 按下 ----------------
while True:
    if keyboard.is_pressed('f1'):
        print(" F1 按下，停止记录...")
        listener.stop()
        break
    time.sleep(0.0015)  # 防止CPU占满

# 记录结束时间
time_stop = time.time()

# 保存到 CSV
with open('save/click_row.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([(time_stop - time_start) / len(mouse_events)] if mouse_events else [0])
    for event in mouse_events:
        csv_writer.writerow(event)

print(" 文件已保存到 save/click_row.csv")
