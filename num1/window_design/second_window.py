import tkinter as tk
import os
import re


class MainWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)  # 设置parent为self的父容器
        self.parent = parent
        self.work_path = "save"
        self.saved_list = os.listdir(self.work_path)

    def record_start(self):
        pass