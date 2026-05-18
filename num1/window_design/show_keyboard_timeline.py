import tkinter as tk
from tkinter import messagebox, simpledialog
import ast
import os


class KeyboardTimelineViewer:
    def __init__(self, parent=None):
        if parent is None:
            self.root = tk.Tk()
            self.window = self.root
        else:
            self.root = parent
            self.window = tk.Toplevel(parent)

        self.window.title("键盘可视化时间线")
        self.window.geometry("1000x400")

        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.y_start = 120
        self.line_len = 60
        self.overlap_threshold = 20  # 重叠判定距离20像素

        # 拖动相关状态变量
        self.drag_data = {
            "is_dragging": False,
            "element_id": None,
            "start_x": 0,
            "offset_x": 0
        }
        self.element_info = {}
        self.current_events = []
        self.current_file = ""
        self.t_max = 0
        self.unsaved_changes = False  # 新增：未保存修改标记

        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-1>", self.on_double_click)
        # 新增：Ctrl+S保存快捷键
        self.window.bind("<Control-s>", self.save_changes)
        # 新增：窗口关闭事件监听
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_and_draw(self, file_path):
        """从文件加载数据并绘制时间线（原draw_timeline拆分）"""
        self.canvas.delete(tk.ALL)
        self.element_info.clear()
        self.current_events = []
        self.current_file = file_path
        self.t_max = 0
        self.unsaved_changes = False  # 加载文件后重置未保存状态

        self.window.update()
        canvas_w = self.canvas.winfo_width() - 20

        if not os.path.exists(file_path):
            self.canvas.create_text(canvas_w / 2, 150, text="文件不存在", fill="red", font=("Arial", 14))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                key, times = ast.literal_eval(line)
                t0, t1 = times[0], times[1]
                self.current_events.append((key, t0, t1))

        if not self.current_events:
            self.canvas.create_text(canvas_w / 2, 150, text="无按键数据", fill="gray")
            return

        self.t_max = max(e[2] for e in self.current_events)
        self.redraw_timeline()

    def redraw_timeline(self):
        """基于当前内存中的数据重新绘制时间线（不读取文件）"""
        self.canvas.delete(tk.ALL)
        self.element_info.clear()
        self.window.update()
        canvas_w = self.canvas.winfo_width() - 20

        if not self.current_events:
            return

        self.t_max = max(e[2] for e in self.current_events)  # 重新计算最大时间

        # 绘制主时间线
        self.canvas.create_line(20, self.y_start, canvas_w, self.y_start, fill="black", width=2)

        # 绘制刻度
        step = max(100, self.t_max // 10)
        for t in range(0, self.t_max + step, step):
            x = t / self.t_max * canvas_w
            self.canvas.create_line(x, self.y_start - 8, x, self.y_start + 8, fill="black")
            self.canvas.create_text(x, self.y_start + 20, text=f"{t}", font=("Arial", 9))

        # 绘制按键事件
        gap = 0
        for idx, (key, t0, t1) in enumerate(self.current_events):
            x0 = t0 / self.t_max * canvas_w
            x1 = t1 / self.t_max * canvas_w
            mid_x = (x0 + x1) / 2

            # 按下事件
            press_line = self.canvas.create_line(
                x0, self.y_start - self.line_len // 2,
                x0, self.y_start + self.line_len // 2,
                fill="black", width=2
            )
            self.element_info[press_line] = (idx, 't0')

            press_arrow = self.canvas.create_text(
                x0 + 8, self.y_start - self.line_len // 2 - gap,
                text="←", font=("Arial", 12, "bold"), fill="#222222"
            )
            self.element_info[press_arrow] = (idx, 'arrow_t0')

            time_y_original = self.y_start + self.line_len // 2 + 15
            press_time = self.canvas.create_text(
                x0, time_y_original,
                text=f"{t0}", font=("Arial", 8), fill="#555555"
            )
            self.element_info[press_time] = (idx, 'time_t0', time_y_original)

            # 抬起事件
            release_line = self.canvas.create_line(
                x1, self.y_start - self.line_len // 2,
                x1, self.y_start + self.line_len // 2,
                fill="black", width=2
            )
            self.element_info[release_line] = (idx, 't1')

            release_arrow = self.canvas.create_text(
                x1 - 8, self.y_start - self.line_len // 2 - gap,
                text="→", font=("Arial", 12, "bold"), fill="#222222"
            )
            self.element_info[release_arrow] = (idx, 'arrow_t1')

            release_time = self.canvas.create_text(
                x1, time_y_original,
                text=f"{t1}", font=("Arial", 8), fill="#555555"
            )
            self.element_info[release_time] = (idx, 'time_t1', time_y_original)

            # 按键名称
            key_text = self.canvas.create_text(
                mid_x, self.y_start - self.line_len // 2 - gap,
                text=key, font=("Arial", 10, "bold")
            )
            self.element_info[key_text] = (idx, 'text')

            gap = -10 if gap == 0 else 0

        self.adjust_time_labels()

    def adjust_time_labels(self):
        time_labels = []
        for elem_id, info in self.element_info.items():
            if info[1].startswith('time_'):
                x = self.canvas.coords(elem_id)[0]
                original_y = info[2]
                time_labels.append((x, elem_id, original_y))

        time_labels.sort(key=lambda x: x[0])

        for i in range(1, len(time_labels)):
            prev_x, prev_elem, prev_original_y = time_labels[i - 1]
            curr_x, curr_elem, curr_original_y = time_labels[i]
            distance = curr_x - prev_x

            if distance < self.overlap_threshold:
                upper_y = self.y_start - self.line_len // 2 - 15
                self.canvas.coords(curr_elem, curr_x, upper_y)
            else:
                self.canvas.coords(curr_elem, curr_x, curr_original_y)

    def on_press(self, event):
        element_id = self.canvas.find_closest(event.x, event.y)[0]
        if element_id in self.element_info and self.element_info[element_id][1] in ['t0', 't1']:
            self.drag_data["is_dragging"] = True
            self.drag_data["element_id"] = element_id
            self.drag_data["start_x"] = event.x
            line_coords = self.canvas.coords(element_id)
            self.drag_data["offset_x"] = event.x - line_coords[0]

    def on_drag(self, event):
        if not self.drag_data["is_dragging"]:
            return

        canvas_w = self.canvas.winfo_width() - 20
        new_x = max(0, min(event.x - self.drag_data["offset_x"], canvas_w))

        element_id = self.drag_data["element_id"]
        event_idx, time_type = self.element_info[element_id]

        # 更新竖线位置
        line_coords = self.canvas.coords(element_id)
        self.canvas.coords(element_id, new_x, line_coords[1], new_x, line_coords[3])

        # 更新箭头和时间文字
        for elem_id, info in self.element_info.items():
            idx = info[0]
            typ = info[1]
            if idx != event_idx:
                continue

            if typ == f'arrow_{time_type}':
                offset = 8 if time_type == 't0' else -8
                arrow_coords = self.canvas.coords(elem_id)
                self.canvas.coords(elem_id, new_x + offset, arrow_coords[1])

            elif typ == f'time_{time_type}':
                time_coords = self.canvas.coords(elem_id)
                self.canvas.coords(elem_id, new_x, time_coords[1])

        # 更新按键名称
        key, t0, t1 = self.current_events[event_idx]
        x0 = t0 / self.t_max * canvas_w if time_type != 't0' else new_x
        x1 = t1 / self.t_max * canvas_w if time_type != 't1' else new_x
        mid_x = (x0 + x1) / 2

        for elem_id, info in self.element_info.items():
            idx = info[0]
            typ = info[1]
            if idx == event_idx and typ == 'text':
                text_coords = self.canvas.coords(elem_id)
                self.canvas.coords(elem_id, mid_x, text_coords[1])
                break

        self.adjust_time_labels()

    def on_release(self, event):
        if not self.drag_data["is_dragging"]:
            self.drag_data = {"is_dragging": False, "element_id": None, "start_x": 0, "offset_x": 0}
            return

        element_id = self.drag_data["element_id"]
        line_coords = self.canvas.coords(element_id)
        new_x = line_coords[0]
        canvas_w = self.canvas.winfo_width() - 20
        new_time = round(new_x * self.t_max / canvas_w)

        event_idx, time_type = self.element_info[element_id]
        key, t0, t1 = self.current_events[event_idx]

        # 时间合法性校验
        if time_type == 't0':
            new_t0 = max(0, min(new_time, t1))
            self.current_events[event_idx] = (key, new_t0, t1)
            final_time = new_t0
        else:
            new_t1 = max(t0, new_time)
            self.current_events[event_idx] = (key, t0, new_t1)
            final_time = new_t1

        # 更新时间文字
        for elem_id, info in self.element_info.items():
            idx = info[0]
            typ = info[1]
            if idx == event_idx and typ == f'time_{time_type}':
                self.canvas.itemconfig(elem_id, text=str(final_time))
                break

        self.adjust_time_labels()
        self.unsaved_changes = True  # 标记有未保存修改
        self.drag_data = {"is_dragging": False, "element_id": None, "start_x": 0, "offset_x": 0}

    def on_double_click(self, event):
        """双击时间标签修改时间功能"""
        element_id = self.canvas.find_closest(event.x, event.y)[0]
        if element_id not in self.element_info:
            return

        info = self.element_info[element_id]
        typ = info[1]
        if not typ.startswith('time_'):
            return  # 仅响应时间标签的双击

        event_idx = info[0]
        time_type = typ.split('_')[1]  # 提取t0/t1
        key, t0, t1 = self.current_events[event_idx]
        current_time = t0 if time_type == 't0' else t1
        action = "按下" if time_type == 't0' else "抬起"

        # 弹出输入对话框
        new_time = simpledialog.askinteger(
            "修改时间",
            f"请输入【{key}】键的{action}时间（毫秒）：",
            initialvalue=current_time,
            minvalue=0
        )

        if new_time is None:
            return  # 用户取消输入

        # 时间合法性校验
        if time_type == 't0':
            if new_time > t1:
                messagebox.showerror("输入错误", "按下时间不能大于抬起时间！")
                return
            self.current_events[event_idx] = (key, new_time, t1)
        else:
            if new_time < t0:
                messagebox.showerror("输入错误", "抬起时间不能小于按下时间！")
                return
            self.current_events[event_idx] = (key, t0, new_time)

        self.unsaved_changes = True  # 标记有未保存修改
        self.redraw_timeline()  # 重新绘制界面（不读取文件）

    def save_changes(self, event=None):
        """Ctrl+S保存修改到文件"""
        if self.unsaved_changes and self.current_file:
            self._write_events_to_file()
            self.unsaved_changes = False
            messagebox.showinfo("保存成功", "修改已保存到文件")

    def on_close(self):
        """窗口关闭事件：检查未保存修改并提示"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "未保存的修改",
                "您有未保存的修改，是否保存后再关闭？",
                default=messagebox.YES
            )
            if result is None:  # 用户点击取消
                return
            elif result:  # 用户选择保存
                self._write_events_to_file()
        self.window.destroy()

    def _write_events_to_file(self):
        """将内存中的数据写入文件"""
        if not self.current_file or not self.current_events:
            return

        with open(self.current_file, "w", encoding="utf-8") as f:
            for key, t0, t1 in self.current_events:
                f.write(f"('{key}', ({t0}, {t1}))\n")


if __name__ == '__main__':
    viewer = KeyboardTimelineViewer()
    viewer.load_and_draw("../save/dir1/save2.txt")  # 原draw_timeline改名为load_and_draw
    viewer.window.mainloop()