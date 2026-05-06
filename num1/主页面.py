import sys
import tkinter as tk
from window_design.show_mouse_movement import Window_mouse  # 假设文件存在并且类定义无误
from window_design.main_window import MainWindow  # 假设文件存在并且类定义无误

class Main:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.current_frame = None
        self.temple_root = None
        self.root.overrideredirect(True)

        # 保持中心出现
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 创建导航按钮区域+拖动效果+最小化最大化，关闭窗口
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.configure(background="#87CEEB")
        self.nav_frame.pack(side=tk.TOP, fill=tk.X)
        self.nav_frame.bind("<Button-1>", self.start_move)
        self.nav_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.nav_frame.bind("<B1-Motion>", self.do_move)

        self.is_maximized = False

        self.buttons_names = [
            ("✕", self.closing_func, "closing_button"),
            ("🗖", self.max_root_func, "max_button"),
            ("—", self.min_root_func, "min_button"),
            ("页面 1", self.show_page1, "show_page1_button"),
            ("页面 2", self.show_page2, "show_page2_button")
        ]
        self.buttons = dict()
        # 使用 for 循环创建按钮并绑定事件
        for text, command, index in self.buttons_names:
            button = tk.Button(self.nav_frame, bg="#87CEEB", relief="flat", text=text, command=command)
            button.pack(side=tk.RIGHT if text in ("✕", "🗖", "—") else tk.LEFT, fill=tk.Y, padx=5, pady=5)
            button.bind("<Enter>", self.on_button_enter)
            button.bind("<Leave>", self.on_button_leave)
            button.bind("<Button-1>", lambda event, func=command: self.on_button_click(event, func))
            self.buttons[index] = button

        # 创建内容显示区域
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 默认显示页面1
        self.show_page1()

    def on_button_click(self, event, func):
        func()  # 触发 command 指定的函数

    def closing_func(self):
        self.root.destroy()
        sys.exit()

    def max_root_func(self):
        if not self.is_maximized:
            # 最大化窗口
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.is_maximized = True
            self.buttons["max_button"].config(text="🗗")
        else:
            # 还原窗口
            self.root.geometry("600x400")
            self.is_maximized = False
            self.buttons["max_button"].config(text="🗖")

    def min_root_func(self):
        pass

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.root.winfo_x() + deltax
        new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{int(new_x)}+{int(new_y)}")

    def on_button_enter(self, event):
        # 鼠标进入按钮区域时的处理
        widget = event.widget
        widget.config(bg="#B0E0E6")

    def on_button_leave(self, event):
        # 鼠标离开按钮区域时的处理
        widget = event.widget
        widget.config(bg="#87CEEB")

    def switch_frame(self, new_frame):
        if self.current_frame is not None:
            self.current_frame.pack_forget()  # 隐藏当前Frame
        self.current_frame = new_frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)  # 显示新Frame

    def show_page1(self):
        frame1 = MainWindow(self.content_frame)
        self.switch_frame(frame1)

    def show_page2(self):
        if self.temple_root is not None:
            return
        elif self.temple_root is None:
            self.temple_root = tk.Tk()
            Window_mouse(self.temple_root)
            self.temple_root = None


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
