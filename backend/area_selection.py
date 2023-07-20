from pynput.mouse import Listener
import keyboard
from time import sleep


def on_press(x, y, button, pressed):
    global x1, y1, x2, y2
    if pressed:
        print(f'Pressed at {x, y}')
        x1, y1 = x, y
    else:
        x2, y2 = x, y
        print(f'Released at {x, y}')

    if not pressed:
        # Stop listener
        listener.stop()


def start_mouse_listener():
    global listener
    with Listener(on_click=on_press) as listener:
        listener.join()


while True:
    if keyboard.is_pressed('z'):
        start_mouse_listener()
    sleep(0.01)
