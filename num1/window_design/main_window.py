import tkinter as tk
import os
import re
import json
import threading  # 新增：多线程库
from tkinter import messagebox
from put_keyboard import react_keyboard
from put_mouse_event import MousePlayer
from show_mouse_movement import Window_mouse


class MainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.work_path = "../save"

        self.load_window_config()

        if not os.path.exists(self.work_path):
            os.mkdir(self.work_path)

        self.saved_list = os.listdir(self.work_path)
        self.chosen_index = 0
        self.chosen_show_signal = None

        self.List1 = tk.Listbox(self, width=25)
        self.label = tk.Label(self, text="未选择任何文件")
        self.button1 = tk.Button(self, text="执行选中脚本")

        self.mouse_player_root = None
        self.mouse_player = None

        self.packing()

    # 鼠标窗口关闭：只隐藏，不退出程序
    def close_mouse_window(self):
        if self.mouse_player_root:
            self.mouse_player_root.withdraw()

    def load_window_config(self):
        config_path = "../param/controller.json"
        default_width = 500
        default_height = 500

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            width = int(config.get("width", default_width))
            height = int(config.get("height", default_height))
        except:
            width = default_width
            height = default_height

        self.parent.geometry(f"{width}x{height}")

    def on_item_click(self, label1, event):
        try:
            index = event.widget.curselection()[0]
            self.chosen_index = index
            value = event.widget.get(index)
            label1.config(text=f"已选择：{value}")
        except IndexError:
            pass

    def rename_item(self, index, entry, text):
        new_text = entry.get().strip()
        if not new_text:
            entry.destroy()
            return

        self.List1.delete(index)
        self.List1.insert(index, new_text)
        entry.destroy()

        for filename in self.saved_list:
            base, ext = os.path.splitext(filename)
            if base == text:
                old_path = os.path.join(self.work_path, filename)
                new_path = os.path.join(self.work_path, new_text + ext)
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)

        self.refresh_list()

    def change_names(self, event):
        index = self.List1.nearest(event.y)
        text = self.List1.get(index)
        entry = tk.Entry(self)
        entry.insert(0, text)
        entry.place(x=event.x, y=event.y)
        entry.focus_set()
        entry.bind("<Return>", lambda e: self.rename_item(index, entry, text))
        entry.bind("<FocusOut>", lambda e: self.rename_item(index, entry, text))

    def refresh_list(self):
        self.List1.delete(0, tk.END)
        self.saved_list = os.listdir(self.work_path)
        for file_name in self.saved_list:
            self.List1.insert(tk.END, file_name)

    def insert_saved_files(self, listbox):
        self.refresh_list()

    # ========== 【核心修改】并行执行文件夹内文件 ==========
    def play(self):
        path = os.path.join(self.work_path, self.List1.get(self.chosen_index))
        print("执行：", path)
        if not os.path.exists(path):
            return "error"

        # 处理文件夹 → 多线程并行执行
        if os.path.isdir(path):
            files = os.listdir(path)
            found = False
            thread_list = []  # 线程列表

            for f in files:
                fp = os.path.join(path, f)
                if not os.path.isfile(fp):
                    continue

                # TXT文件：创建线程执行键盘操作
                if f.lower().endswith(".txt"):
                    t = threading.Thread(target=react_keyboard, args=(fp,), daemon=True)
                    thread_list.append(t)
                    found = True
                # CSV文件：创建线程执行鼠标操作
                elif f.lower().endswith(".csv"):
                    # 封装函数，因为MousePlayer需要实例化
                    def run_csv(csv_path):
                        player = MousePlayer()
                        player.play(csv_path)

                    t = threading.Thread(target=run_csv, args=(fp,), daemon=True)
                    thread_list.append(t)
                    found = True

            # 启动所有线程，并行执行
            for t in thread_list:
                t.start()

            if not found:
                return "error"

        # 处理单个文件（保持原样）
        elif os.path.isfile(path):
            if path.lower().endswith(".txt"):
                react_keyboard(path)
            elif path.lower().endswith(".csv"):
                player = MousePlayer()
                player.play(path)
            else:
                return "error"
        else:
            return "error"
        return "success"

    def close_menu(self, event=None):
        if self.chosen_show_signal:
            self.chosen_show_signal.destroy()
            self.chosen_show_signal = None

    def show_time(self, event):
        index = self.List1.nearest(event.y)
        if index < 0:
            return
        self.List1.selection_clear(0, tk.END)
        self.List1.selection_set(index)
        self.chosen_index = index

        self.close_menu()

        x = self.winfo_pointerx() + 10
        y = self.winfo_pointery() + 10
        self.chosen_show_signal = tk.Toplevel(self)
        self.chosen_show_signal.geometry(f"200x80+{x}+{y}")
        self.chosen_show_signal.overrideredirect(True)
        self.chosen_show_signal.attributes("-topmost", True)
        self.chosen_show_signal.bind("<FocusOut>", self.close_menu)
        self.chosen_show_signal.bind("<Button-1>", self.close_menu)

        lb = tk.Listbox(self.chosen_show_signal, height=2)
        lb.insert(0, "查看键盘录制")
        lb.insert(1, "查看鼠标轨迹")
        lb.pack(fill=tk.BOTH, expand=True)
        lb.bind("<<ListboxSelect>>", self.shown_save)
        lb.focus_set()

    def shown_save(self, event):
        idx = event.widget.curselection()[0]
        opt = event.widget.get(idx)
        file_name = self.List1.get(self.chosen_index)
        file_path = os.path.join(self.work_path, file_name)

        print(f"选择：{opt}，文件：{file_name}")
        self.close_menu()

        if opt == "查看键盘录制":
            if not file_path.endswith(".txt"):
                messagebox.showerror("错误", "仅支持查看TXT键盘文件！")
                return
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    messagebox.showinfo("键盘录制", f.read())
            except:
                messagebox.showerror("错误", "读取文件失败")

        elif opt == "查看鼠标轨迹":
            if not file_path.endswith(".csv"):
                messagebox.showerror("错误", "仅支持查看CSV鼠标轨迹文件！")
                return

            if self.mouse_player_root is None:
                self.mouse_player_root = tk.Toplevel(self.parent)
                self.mouse_player_root.protocol("WM_DELETE_WINDOW", self.close_mouse_window)
                self.mouse_player = Window_mouse(self.mouse_player_root)

            self.mouse_player_root.deiconify()
            self.mouse_player.start_show_mouse_movement(file_path)

    def packing(self):
        self.insert_saved_files(self.List1)

        self.List1.bind("<<ListboxSelect>>", lambda e: self.on_item_click(self.label, e))
        self.List1.bind("<Double-1>", self.change_names)
        self.List1.bind("<Button-3>", self.show_time)

        self.List1.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.label.pack(pady=10)
        self.button1.pack(pady=5)
        self.button1.config(command=self.play)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("鼠标键盘录制管理器")
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()