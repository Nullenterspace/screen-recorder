import tkinter as tk
from ctypes import windll, wintypes, byref
import sys
import json
import csv
from scipy.spatial import KDTree
import keyboard
from PIL import Image, ImageTk
import time


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Window_mouse:
    def __init__(self, root):
        # 存储完整的鼠标数据：[(x,y,左键,右键,滚轮), ...]
        self.mouse_data = []
        self.draw_position = []  # 仅用于绘制轨迹的x/y

        self.root = root
        self.root.overrideredirect(False)
        self.root.attributes('-alpha', 0.5)
        self.root.attributes('-transparentcolor', 'white')
        self.root.configure(bg='white')
        self.root.wm_attributes('-topmost', 1)
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        hwnd = windll.user32.GetParent(self.root.winfo_id())
        extended_style = windll.user32.GetWindowLongW(hwnd, -20)
        windll.user32.SetWindowLongW(hwnd, -20, extended_style | 0x80000 | 0x20)
        windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

        # 鼠标图标
        self.time_step = 0
        img_mouse = Image.open('../util/img/mouse.png')
        img_mouse.thumbnail((20, 20), Image.Resampling.LANCZOS)
        self.img_mouse = ImageTk.PhotoImage(img_mouse)
        self.img_mouse_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_mouse)

        # 按键状态标记（用于可视化）
        self.key_mark_id = None

        self.pause = True
        self.index = 0

        # 时间窗口
        self.time_win = tk.Toplevel(self.root)
        self.time_win.overrideredirect(True)
        self.time_win.geometry("200x50+10+10")
        self.time_win.wm_attributes('-topmost', 1)
        self.time_win.attributes('-alpha', 1)
        self.time_win.configure(bg="black")
        self.time_label = tk.Label(self.time_win, text="时间: 0.0000s",
                                   font=("微软雅黑", 14), fg="white", bg="black")
        self.time_label.pack(expand=True, fill='both')

        # 鼠标悬浮提示窗口
        self.tip_win = tk.Toplevel(self.root)
        self.tip_win.overrideredirect(True)
        self.tip_win.wm_attributes('-topmost', True)
        self.tip_win.configure(bg="#222")
        self.tip_label = tk.Label(self.tip_win, font=("微软雅黑", 11),
                                  fg="white", bg="#222", padx=8, pady=4)
        self.tip_label.pack()
        self.tip_win.withdraw()

        # 鼠标高亮配置
        self.kdtree = None
        self.highlight_id = None
        self.detect_radius = 30
        # 参数
        self.frame_interval = 0.0015
        self.window_scale = 1.5  # 系统默认1.5

        keyboard.on_press_key("space", self.toggle_pause)
        self.load_param()
        self.draw_movement()
        self.start_mouse_listener()

    def load_param(self):
        with open("../param/frame_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        self.frame_interval = config["frame_interval"]
        self.window_scale = config["window_scale"]

    # 实时监听鼠标
    def start_mouse_listener(self):
        if not self.kdtree:
            self.root.after(50, self.start_mouse_listener)
            return

        mx = self.root.winfo_pointerx()
        my = self.root.winfo_pointery()
        dist, idx = self.kdtree.query([mx, my])

        if dist < self.detect_radius:
            x, y = self.draw_position[idx]
            self.highlight_point(x, y)
            # 显示包含按键状态的提示
            self.show_tip(mx, my, idx, dist)
        else:
            self.clear_highlight()
            self.hide_tip()

        self.root.after(50, self.start_mouse_listener)

    # 鼠标旁显示小窗口（新增按键/滚轮信息）
    def show_tip(self, mx, my, idx, dist):
        if idx >= len(self.mouse_data):
            return
        t = idx * 0.0015
        # 获取录制的按键状态
        left = "按下" if self.mouse_data[idx][2] == 1 else "松开"
        right = "按下" if self.mouse_data[idx][3] == 1 else "松开"
        scroll = "上滚" if self.mouse_data[idx][4] == 1 else "下滚" if self.mouse_data[idx][4] == -1 else "无"

        info = (
            f"序号：{idx}\n"
            f"时间：{t:.3f}s\n"
            f"距离：{dist:.1f}\n"
            f"左键：{left}\n"
            f"右键：{right}\n"
            f"滚轮：{scroll}"
        )
        self.tip_label.config(text=info)
        self.tip_win.geometry(f"+{mx + 15}+{my + 15}")
        self.tip_win.deiconify()

    def hide_tip(self):
        self.tip_win.withdraw()

    # 高亮轨迹点
    def highlight_point(self, x, y):
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
        r = 6
        self.highlight_id = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline="yellow", width=4, fill=""
        )

    def clear_highlight(self):
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None

    # 切换暂停
    def toggle_pause(self, event):
        self.pause = not self.pause
        if not self.pause:
            self.move_step(self.index, self.img_mouse_id)

    # 播放步骤（新增按键状态可视化）
    def move_step(self, index, img_mouse_id):
        self.time_step = index * 0.0015
        self.time_label.config(text=f"时间: {self.time_step:.4f}s")

        if self.pause:
            self.index = index
            return

        if index >= len(self.mouse_data):
            self.pause = True
            return

        # 获取当前帧的完整数据
        x1, y1, left, right, scroll = self.mouse_data[index]
        self.canvas.moveto(img_mouse_id, int(x1), int(y1))

        # 绘制按键状态标记（左键红圈、右键绿圈、滚轮蓝圈）
        self.draw_key_state(x1, y1, left, right, scroll)

        print(f"帧{index}: x={x1}, y={y1}, 左键={left}, 右键={right}, 滚轮={scroll}")
        time.sleep(self.frame_interval - 0.001)
        self.canvas.after(1, self.move_step, index + 1, img_mouse_id)

    # 绘制按键状态标记
    def draw_key_state(self, x, y, left, right, scroll):
        # 清除上一帧的按键标记
        if self.key_mark_id:
            self.canvas.delete(self.key_mark_id)
            self.key_mark_id = None

        r = 8
        # 左键按下：红色实心圆
        if left == 1:
            self.key_mark_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline="red", width=2, fill="red"
            )
        # 右键按下：绿色实心圆
        elif right == 1:
            self.key_mark_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline="green", width=2, fill="green"
            )
        # 滚轮触发：蓝色空心圆
        elif scroll != 0:
            self.key_mark_id = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline="blue", width=3, fill=""
            )

    def on_closing(self):
        self.root.destroy()
        sys.exit()

    def draw_movement(self):
        self.show_mouse_movement()
        # 绘制轨迹线（仅用x/y）
        for i in range(len(self.draw_position) - 1):
            x1, y1 = self.draw_position[i]
            x2, y2 = self.draw_position[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, width=4, fill="blue")
            if i == 1:
                self.canvas.create_text(x1, y1, text="起点", font=("Arial", 24), fill="yellow")
            if i == len(self.draw_position) - 2:
                self.canvas.create_text(x2, y2, text="终点", font=("Arial", 24), fill="yellow")
        self.kdtree = KDTree(self.draw_position)
        self.move_step(0, self.img_mouse_id)

    # 读取完整的CSV数据（保留5列）
    def show_mouse_movement(self):
        with open("../save/mouse_movement.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                # 解析5列数据：x/y（缩放）、左键、右键、滚轮
                x = float(row[0]) / self.window_scale
                y = float(row[1]) / self.window_scale
                left = int(row[2])
                right = int(row[3])
                scroll = int(row[4])

                self.mouse_data.append([x, y, left, right, scroll])
                self.draw_position.append([x, y])  # 轨迹绘制仅用x/y


if __name__ == '__main__':
    root = tk.Tk()
    win = Window_mouse(root)
    root.mainloop()
