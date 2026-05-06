@echo off
set loop_count=100
set python_exe=C:\ProgramData\anaconda3\python.exe

for /l %%i in (1, 1, %loop_count%) do (
    %python_exe% put_keyboard.py save/save2.txt
)

