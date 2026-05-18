from pynput import mouse
import keyboard
import csv
import time
import os
import json


class MouseRecorder:
    def __init__(self):
        # 配置初始化
        if not os.path.exists("save"):
            os.makedirs("save")

        with open("param/frame_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        self.frame_interval = config["frame_interval"]
        self.stop_button = config["stop_button"]

        # 鼠标状态变量
        self.current_x = 0
        self.current_y = 0
        self.left_state = 0
        self.right_state = 0
        self.scroll_state = 0
        self.last_scroll_time = 0
        self.mouse_movement = []
        self.start_time = time.time()
        self.listener = None

    # 鼠标移动监听
    def on_move(self, x, y):
        self.current_x = x
        self.current_y = y

    # 鼠标点击监听
    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.left_state = 1 if pressed else 0
        if button == mouse.Button.right:
            self.right_state = 1 if pressed else 0

    # 鼠标滚轮监听
    def on_scroll(self, x, y, dx, dy):
        self.scroll_state = dy
        self.last_scroll_time = time.time()
        print('Scrolled at ({0}, {1}) with {2} and {3}'.format(x, y, dx, dy))

    # 重置滚轮状态
    def reset_scroll_when_idle(self):
        if time.time() - self.last_scroll_time > 0.1 and self.scroll_state != 0:
            print("stop:", time.time())
            self.scroll_state = 0

    # 开始录制（新增外部路径参数）
    def start_record(self, file_path):
        # 启动监听
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.listener.start()

        print(" 开始录制鼠标，按 F10 停止")
        print(f" 帧间隔：{self.frame_interval}s")

        # 主循环
        while True:
            self.reset_scroll_when_idle()
            if keyboard.is_pressed(self.stop_button):
                print(" 停止录制")
                break

            self.mouse_movement.append([
                self.current_x,
                self.current_y,
                self.left_state,
                self.right_state,
                self.scroll_state
            ])
            time.sleep(self.frame_interval)

        self.listener.stop()
        self.save_to_csv(file_path)

    # 保存CSV文件（接收外部路径参数）
    def save_to_csv(self, file_path):
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            print(len(self.mouse_movement))
            for event in self.mouse_movement:
                if event[0] != 0 or event[1] != 0:
                    csv_writer.writerow(event)
        print(f" 保存完成：{file_path}")


# 启动录制（外部传入路径）
if __name__ == '__main__':
    recorder = MouseRecorder()
    # 外部自定义保存路径，自由修改
    recorder.start_record(file_path="save/mouse_movement.csv")
