import keyboard
import multiprocessing
import time
import sys
import pyautogui

time_begin = 0


def auto_create(name: str, time_start: float, time_end: float):
    p = multiprocessing.Process(target=press_key_process, args=(name.replace(' ', ""), time_start, time_end))
    p.start()


def press_key_process(name: str, time_start: float, time_end: float):
    time1 = time.time()
    print("start", name, time_start, time_end)
    # keyboard.press(name)
    pyautogui.keyDown(name)
    while 1:
        time2 = time.time()
        if int((time2 - time1) * 1000) > (time_end - time_start):
            # keyboard.release(name)
            pyautogui.keyUp(name)
            print("release", name)
            break
    # multiprocessing.current_process().terminate()


def react_keyboard(file_name):
    all_keys = []
    with open(file_name, 'r') as file:
        str_list = file.readlines()
        # print(str_list)
        for i in str_list:
            this_list = eval(i)
            all_keys.append(this_list)

    next_key_index = 0
    next_key = all_keys[next_key_index]
    print("put_keyboard", time.time())

    global time_begin
    time_begin = time.time()
    while 1:
        current_time = int((time.time() - time_begin) * 1000)
        if current_time > next_key[1][0]:
            auto_create(str(next_key[0]), next_key[1][0], next_key[1][1])
            next_key_index += 1
            if next_key_index == len(all_keys):
                break
            next_key = all_keys[next_key_index]


def put_keyboard(file_name):

    react_keyboard(file_name)


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("Usage: python script_name.py <file_name>")
    #     sys.exit(1)
    # file_name = sys.argv[1]
    react_keyboard("save/dir1/save2.txt")
