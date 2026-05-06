import keyboard
import time
import re
keyboard_input = []
time_count_signal = 0


def add_delete(x):
    print(x)
    matches = re.findall(r'\((.*?)\)', str(x))
    global time_count_signal
    time_start = time.time()
    time_start = int(time_start*1000)
    if not keyboard_input:
        time_count_signal = time_start
        keyboard_input.append([matches[0], [time_start - time_count_signal]])
    elif 'down' in matches[0]:
        for i in keyboard_input:
            if i[0] == matches[0]:
                return
        keyboard_input.append([matches[0], [time_start - time_count_signal]])
    elif 'up' in matches[0]:
        for i in range(len(keyboard_input)-1, 0,  -1):
            print(matches[0].replace('up', 'down'), "   r   ", keyboard_input[i][0])
            if keyboard_input[i][0] == matches[0].replace('up', 'down'):
                keyboard_input[i][-1].append(time_start - time_count_signal)
                print("UP_down", keyboard_input[i][0])
                keyboard_input[i][0] = keyboard_input[i][0].replace('down', "")


def find_last_same_key(key_list, name):
    for i in range(key_list, -1):
        if key_list[i][1] == name - 'down' + 'up':
            return key_list[-1]


def record_words(file_name):
    keyboard.hook(lambda x: add_delete(x))
    keyboard.wait('scroll_lock')

    with open(file_name, 'w') as file:
        for i in range(1, len(keyboard_input)-1):
            print(str(keyboard_input[i]))
            file.write(str(keyboard_input[i]) + '\n')


if __name__ == '__main__':
    record_words("save/save2.txt")
