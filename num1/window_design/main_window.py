import tkinter as tk
import os
import re


class MainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)  # 设置parent为self的父容器
        self.parent = parent
        self.work_path = "save"
        self.saved_list = os.listdir(self.work_path)
        self.chosen_index = 0

        self.List1 = tk.Listbox(self, width=20)
        self.label = tk.Label(self)
        self.button1 = tk.Button(self, text="执行")

        self.packing()  # 确保初始化后进行布局
        self.chosen_show_signal = None  # 这个是右键展示鼠标和按键记录的

    def on_item_click(self, label1, event):
        index = event.widget.curselection()[0]  # 获取当前选中项的索引
        self.chosen_index = index
        value = event.widget.get(index)  # 获取选中项的值
        label1.config(text=f"Clicked: {value}")

    def rename_item(self, index, entry, text):
        # 获取Entry小部件中的文本
        new_text = entry.get()
        # 更新Listbox中的项
        self.List1.delete(index)
        self.List1.insert(index, new_text)
        # 销毁Entry小部件
        entry.destroy()
        for i in self.saved_list:
            base_name, extension = os.path.splitext(i)
            if text == base_name:
                os.rename(self.work_path + "\\" + i, self.work_path + "\\" + new_text + extension)

    def change_names(self, event):
        index = self.List1.nearest(event.y)
        text = self.List1.get(index)
        entry = tk.Entry(self)
        entry.insert(0, text)
        entry.place(x=event.x, y=event.y)
        # 绑定回车键事件处理函数
        entry.bind("<Return>", lambda e: self.rename_item(index, entry, text))
        # 绑定失去焦点事件处理函数
        entry.bind("<FocusOut>", lambda e: self.rename_item(index, entry, text))
        # 设置焦点到Entry小部件
        entry.focus_set()

    def insert_saved_files(self, listbox):
        all_files = []
        for i in self.saved_list:
            i = re.sub(r'\.[^.]*$', '', i)
            if i not in all_files:
                all_files.append(i)
        for i in all_files:
            listbox.insert(tk.END, i)

    def play(self):
        text = self.List1.get(self.chosen_index)
        for i in self.saved_list:
            base_name, extension = os.path.splitext(i)
            if text == base_name:
                pass

    def show_time(self, event):
        index = self.List1.nearest(event.y)
        text = self.List1.get(index)
        print(text)
        if self.chosen_show_signal is not None:
            self.chosen_show_signal.destroy()
            self.chosen_show_signal = None
        if self.chosen_show_signal is None:
            self.update_idletasks()  # 确保获取的鼠标位置是最新的
            mouse_x = self.winfo_pointerx()
            mouse_y = self.winfo_pointery()
            self.chosen_show_signal = tk.Tk()
            self.chosen_show_signal.geometry(f"120x40+{mouse_x}+{mouse_y}")
            self.chosen_show_signal.overrideredirect(True)
            self.shown_listbox = tk.Listbox(self.chosen_show_signal)

            self.way_to_shown = ["查看键盘录制文件", "查看鼠标录制轨迹"]
            for i in self.way_to_shown:
                self.shown_listbox.insert(tk.END, i)
            self.shown_listbox.pack(side=tk.TOP, fill=tk.BOTH)
            self.shown_listbox.bind("<<ListboxSelect>>", lambda event: self.shown_save(event))

    def shown_save(self, event):
        index = event.widget.curselection()[0]  # 获取当前选中项的索引
        value = event.widget.get(index)  # 获取选中项的值
        print(value)

    def packing(self):
        self.insert_saved_files(self.List1)
        self.List1.bind("<<ListboxSelect>>", lambda event: self.on_item_click(self.label, event))
        self.List1.bind("<Double-Button-1>", self.change_names)
        self.List1.bind("<Button-3>", self.show_time)

        # 设置布局
        self.List1.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.label.pack(side=tk.TOP, padx=10, pady=10)
        self.button1.pack(side=tk.TOP, padx=10, pady=10)
        self.button1.bind("<Button-1>", lambda event: self.play())

