import tkinter as tk

def on_single_click(event):
    global last_click_time
    current_time = event.time
    delta = current_time - last_click_time
    if delta < 300:
        on_double_click(event)
    last_click_time = current_time

def on_double_click(event):
    # 获取双击位置的索引
    index = listbox.nearest(event.y)
    # 获取双击位置的文本
    text = listbox.get(index)
    # 在双击位置创建Entry小部件
    entry = tk.Entry(root)
    entry.insert(0, text)
    entry.place(x=event.x, y=event.y)
    # 绑定回车键事件处理函数
    entry.bind("<Return>", lambda e: rename_item(index, entry))
    # 绑定失去焦点事件处理函数
    entry.bind("<FocusOut>", lambda e: rename_item(index, entry))
    # 设置焦点到Entry小部件
    entry.focus_set()

def rename_item(index, entry):
    # 获取Entry小部件中的文本
    new_text = entry.get()
    # 更新Listbox中的项
    listbox.delete(index)
    listbox.insert(index, new_text)
    # 销毁Entry小部件
    entry.destroy()

root = tk.Tk()

listbox = tk.Listbox(root)
listbox.pack()

listbox.insert(tk.END, "Option 1")
listbox.insert(tk.END, "Option 2")
listbox.insert(tk.END, "Option 3")

# 记录上一次单击的时间
last_click_time = 0
# 绑定单击事件处理函数
listbox.bind("<Button-1>", on_single_click)

root.mainloop()
