# mouse_tracker.py
import math


class MouseTracker:
    def __init__(self, canvas, draw_position):
        self.canvas = canvas
        self.draw_position = draw_position
        self.last_idx = 0
        self.highlight_id = None
        self.first_search = True  # 标记是否第一次搜索

    def track_mouse(self, root):
        if not self.draw_position:
            root.after(50, self.track_mouse, root)
            return

        mx = root.winfo_pointerx()
        my = root.winfo_pointery()
        n = len(self.draw_position)
        best_dist = float('inf')
        best_idx = 0

        # ======================
        # 第一次：全量搜索（只执行一次）
        # ======================
        if self.first_search:
            for i in range(n):
                x, y = self.draw_position[i]
                dx = mx - x
                dy = my - y
                dist = dx * dx + dy * dy
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
            self.first_search = False  # 永远不再进入

        # ======================
        # 后续：只搜索附近 30 个点
        # ======================
        else:
            search_range = 30
            start = max(0, self.last_idx - search_range // 2)
            end = min(n, self.last_idx + search_range // 2)

            for i in range(start, end):
                x, y = self.draw_position[i]
                dx = mx - x
                dy = my - y
                dist = dx * dx + dy * dy
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i

        self.last_idx = best_idx
        real_dist = math.sqrt(best_dist)

        if real_dist < 30:
            print(real_dist)
            x, y = self.draw_position[best_idx]
            self.highlight_point(x, y)
        else:
            self.clear_highlight()

        root.after(50, self.track_mouse, root)

    def highlight_point(self, x, y):
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
        r = 6
        self.highlight_id = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline="yellow",
            width=5,
            fill=""
        )

    def clear_highlight(self):
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None
