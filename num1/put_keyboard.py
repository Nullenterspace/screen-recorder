import keyboard
import multiprocessing
import time
import sys
def auto_create(name: str, time_start: float, time_end: float):
    p = multiprocessing.Process(target=v, args=(name.replace(' ', ""), time_start, time_end))
    p.start()


def v(name: str, time_start: float, time_end: float):

    time1 = time.time()
    print("start", name, time_start, time_end)
    keyboard.press(name)
    while 1:
        time2 = time.time()
        if int((time2 - time1)*1000) > (time_end - time_start):
            keyboard.release(name)
            print("release", name)
            break
    # multiprocessing.current_process().terminate()


def react_keyboard(file_name):
    time.sleep(2)
    all_start_time = []
    with open(file_name, 'r') as file:
        str_list = file.readlines()
        for i in str_list:
            print(eval(i), type(eval(i)))
            this_list = eval(i)
            all_start_time.append(this_list[1][0])
    print(all_start_time)
    time_begin = time.time()
    while 1:
        current_time = int((time.time() - time_begin)*1000)
        current_key = 0
        # print(current_time)
        if current_time in all_start_time or current_time-1 in all_start_time or current_time-2 in all_start_time:
            if current_time in all_start_time:
                current_time = current_time
            elif current_time-1 in all_start_time:
                current_time = current_time-1
            elif current_time-2 in all_start_time:
                current_time = current_time-2
            print("Timeout reached", current_time)
            current_key = eval(str_list[all_start_time.index(current_time)])
            print(current_key)
            all_start_time[all_start_time.index(current_time)] = all_start_time.index(current_time)
            auto_create(current_key[0], current_key[1][0], current_key[1][1])
        if all_start_time[-1] == len(all_start_time)-1:
            break


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_name>")
        sys.exit(1)
    file_name = sys.argv[1]
    react_keyboard(file_name)