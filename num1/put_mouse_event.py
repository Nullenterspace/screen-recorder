import pyautogui
import csv
import json
import time
import os
import keyboard

# 关闭 PyAutoGUI 防呆保护（解决你之前的报错）
pyautogui.FAILSAFE = False

class MousePlayer:
    def __init__(self):
        self.PARAM_FOLDER = "param"
        self.frame_interval = 0.0015
        self.last_left = 0
        self.last_right = 0
        self.load_config()

    def load_config(self):
        """读取帧间隔配置"""
        try:
            config_path = os.path.join(self.PARAM_FOLDER, "frame_config.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.frame_interval = config.get("frame_interval", 0.0015)
        except:
            self.frame_interval = 0.0015

    def load_data(self, csv_file_path):
        """
        从外部传入 CSV 完整路径
        :param csv_file_path: 如 save/123.csv
        """
        data = []
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                x = float(row[0])
                y = float(row[1])
                left = int(row[2])
                right = int(row[3])
                scroll = int(row[4])
                data.append([x, y, left, right, scroll])
        return data

    def play(self, csv_file_path):
        """
        播放指定 CSV 文件
        :param csv_file_path: 外部传入的完整路径
        """
        time_start = time.time()
        data = self.load_data(csv_file_path)
        print(f"开始回放鼠标，共 {len(data)} 帧", time.time())

        self.last_left = 0
        self.last_right = 0

        while True:
            if keyboard.is_pressed('f9'):
                break
            time.sleep(0.01)
        for x, y, left, right, scroll in data:
            pyautogui.moveTo(x, y, _pause=False)

            # 左键
            if left != self.last_left:
                if left == 1:
                    pyautogui.mouseDown(button="left", _pause=False)
                else:
                    pyautogui.mouseUp(button="left", _pause=False)
                self.last_left = left

            # 右键
            if right != self.last_right:
                if right == 1:
                    pyautogui.mouseDown(button="right", _pause=False)
                else:
                    pyautogui.mouseUp(button="right", _pause=False)
                self.last_right = right

            time.sleep(self.frame_interval)

        print("回放完成！", time.time() - time_start)

if __name__ == "__main__":
    # 测试：直接传入文件路径
    player = MousePlayer()
    player.play("save/mouse_movement.csv")