import keyboard
import threading
import time
import pyautogui
import json


class KeyboardSimulator:
    def __init__(self):
        config_path = "param/frame_config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # 安全取值
            self.start_button = config.get("start_play_button", "f9")
        except Exception:
            self.start_button = "f9"
        pass

    def auto_create(self, name: str, time_start: float, time_end: float):
        # 多进程 → 多线程（最大优化，不卡顿）
        t = threading.Thread(
            target=self.press_key_process,
            args=(name.replace(' ', ""), time_start, time_end),
            daemon=True
        )
        t.start()

    def press_key_process(self, name: str, time_start: float, time_end: float):
        time1 = time.time()
        print("start", name, time_start, time_end)
        pyautogui.keyDown(name)

        # 加极短休眠，彻底解决CPU占满问题（不影响按键精度）
        while 1:
            time2 = time.time()
            if int((time2 - time1) * 1000) > (time_end - time_start):
                pyautogui.keyUp(name)
                print("release", name)
                break
            time.sleep(0.001)  # 关键优化，降低CPU占用

    def react_keyboard(self, file_name):
        all_keys = []
        with open(file_name, 'r') as file:
            str_list = file.readlines()
            for i in str_list:
                this_list = eval(i)
                all_keys.append(this_list)

        next_key_index = 0
        next_key = all_keys[next_key_index]
        print("put_keyboard", time.time())

        # 等待F9触发（保留）
        while True:
            if keyboard.is_pressed(self.start_button):
                break
            time.sleep(0.01)

        # 局部变量替代全局变量，避免冲突
        time_begin = time.time()
        while 1:
            current_time = int((time.time() - time_begin) * 1000)
            if current_time > next_key[1][0]:
                self.auto_create(str(next_key[0]), next_key[1][0], next_key[1][1])
                next_key_index += 1
                if next_key_index == len(all_keys):
                    break
                next_key = all_keys[next_key_index]
            time.sleep(0.0005)  # 主线程降CPU

    def put_keyboard(self, file_name):
        self.react_keyboard(file_name)


# 主程序调用（完全保留原有写法）
if __name__ == '__main__':
    simulator = KeyboardSimulator()
    simulator.react_keyboard("save/dir1/save2.txt")