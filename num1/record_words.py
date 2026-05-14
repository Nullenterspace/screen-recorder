import keyboard
import time
import re
import json


class KeyboardRecorder:
    def __init__(self):
        # 原全局变量 → 实例属性（完全保留，不修改逻辑）
        self.keyboard_input = []
        self.time_count_signal = 0
        self.prepare_write = []
        with open("param/frame_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        self.stop_button = config["stop_button"]

    def add_delete(self, x):
        # 原函数代码一字未改
        print(x)
        matches = re.findall(r'\((.*?)\)', str(x))
        time_start = time.time()
        time_start = int(time_start*1000)
        if 'down' in matches[0]:
            self.keyboard_input.append([matches[0], [time_start - self.time_count_signal]])
            print("time_gap", time_start, self.time_count_signal, time_start - self.time_count_signal)
        elif 'up' in matches[0]:
            for i in range(len(self.keyboard_input)-1, -1,  -1):
                if self.keyboard_input[i][0] == matches[0].replace('up', 'down'):
                    self.keyboard_input[i][-1].append(time_start - self.time_count_signal)
                    self.keyboard_input[i][0] = self.keyboard_input[i][0].replace('down', "")

    def record_words(self, file_name):
        # 原函数代码一字未改
        self.time_count_signal = int(time.time()*1000)
        keyboard.hook(lambda x: self.add_delete(x))
        keyboard.wait(self.stop_button)

        with open(file_name, 'w') as file:
            print("Recording")
            print(self.keyboard_input)
            for i in range(0, len(self.keyboard_input)-1):
                file.write(str(self.keyboard_input[i]) + '\n')


if __name__ == '__main__':
    # 调用方式和原逻辑一致
    recorder = KeyboardRecorder()
    recorder.record_words("save/dir2/save2.txt")
