from threading import Thread
from time import sleep
from PIL import Image, ImageGrab

def try_save_image(image):
        try:
            cropped_image = image.crop((250, 770, 1600, 1000))
            cropped_image.save('subs.png', 'png')
            print('Сохранил')
        except Exception as e:
            print('Ошибка при сохранении изображения:', e)

def screen_push():
    last_clipboard_image = ImageGrab.grabclipboard()
    while True:
        clipboard_image = ImageGrab.grabclipboard()
        if clipboard_image is not None and clipboard_image != last_clipboard_image:
            try_save_image(clipboard_image)
            last_clipboard_image = clipboard_image
        sleep(1)

thread = Thread(target=screen_push)
thread.start()
thread.join()
print('thread finished…exiting')