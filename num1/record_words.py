import keyboard
import time
import re
keyboard_input = []
time_count_signal = 0
prepare_write = []

def add_delete(x):
    print(x)
    matches = re.findall(r'\((.*?)\)', str(x))
    global time_count_signal
    global prepare_write
    time_start = time.time()
    time_start = int(time_start*1000)
    if 'down' in matches[0]:
        # for i in keyboard_input:
        #     if i[0] == matches[0]:
        #         return
        keyboard_input.append([matches[0], [time_start - time_count_signal]])
        print("time_gap", time_start, time_count_signal, time_start - time_count_signal)
    elif 'up' in matches[0]:
        for i in range(len(keyboard_input)-1, -1,  -1):
            # print(matches[0].replace('up', 'down'), "   r   ", keyboard_input[i][0])
            if keyboard_input[i][0] == matches[0].replace('up', 'down'):
                keyboard_input[i][-1].append(time_start - time_count_signal)
                # print("UP_down", keyboard_input[i][0])
                keyboard_input[i][0] = keyboard_input[i][0].replace('down', "")


def record_words(file_name):
    global time_count_signal
    time_count_signal = int(time.time()*1000)
    keyboard.hook(lambda x: add_delete(x))
    keyboard.wait('f10')

    with open(file_name, 'w') as file:
        print("Recording")
        print(keyboard_input)
        for i in range(0, len(keyboard_input)-1):
            file.write(str(keyboard_input[i]) + '\n')


if __name__ == '__main__':
    record_words("save/dir1/save2.txt")