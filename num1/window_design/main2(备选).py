import tkinter as tk
from tkinter import messagebox

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("页面切换示例")
        self.root.geometry("600x400")
        self.current_frame = None

        # 创建导航按钮
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(side=tk.TOP, fill=tk.X)

        btn_page1 = tk.Button(self.nav_frame, text="页面 1", command=self.show_page1)
        btn_page1.pack(side=tk.LEFT, padx=5, pady=5)

        btn_page2 = tk.Button(self.nav_frame, text="页面 2", command=self.show_page2)
        btn_page2.pack(side=tk.LEFT, padx=5, pady=5)

        btn_page3 = tk.Button(self.nav_frame, text="页面 3", command=self.show_page3)
        btn_page3.pack(side=tk.LEFT, padx=5, pady=5)

        # 默认显示页面1
        self.show_page1()

    def switch_frame(self, new_frame):
        """切换当前显示的Frame"""
        if self.current_frame is not None:
            self.current_frame.pack_forget()  # 隐藏当前Frame
        self.current_frame = new_frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)  # 显示新Frame

    def show_page1(self):
        frame1 = Page1(self.root, self)
        self.switch_frame(frame1)

    def show_page2(self):
        frame2 = Page2(self.root, self)
        self.switch_frame(frame2)

    def show_page3(self):
        frame3 = Page3(self.root, self)
        self.switch_frame(frame3)

class Page1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="这是页面 1", font=("Arial", 16))
        label.pack(pady=20)

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="这是页面 2", font=("Arial", 16))
        label.pack(pady=20)

        # 添加一个返回按钮以返回页面1
        back_button = tk.Button(self, text="返回页面 1", command=controller.show_page1)
        back_button.pack(pady=10)

class Page3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="这是页面 3", font=("Arial", 16))
        label.pack(pady=20)

        # 添加一个返回按钮以返回页面1
        back_button = tk.Button(self, text="返回页面 1", command=controller.show_page1)
        back_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
