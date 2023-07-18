from threading import Thread
from time import sleep
from PIL import Image, ImageGrab
from googletrans import Translator
import pytesseract
from colorama import Fore
from flask import Flask

custom_conf = r'--psm 11'
translator = Translator()
app = Flask( __name__ )
texts = []

@app.route("/get_new_text")
def hello():
    print('thread front', flush=True)
    global texts
    if len(texts) > 0:
        return texts.pop(0)
    return ""


def translate_image(image):
    global texts
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    result = pytesseract.image_to_string(image, config=custom_conf, output_type='string')
    result = result.replace('\n', ' ')
    print(Fore.RED + '--en--', flush=True)
    print(Fore.RED + result, flush=True)
    translate = translator.translate(result, dest='ru')
    print(Fore.GREEN + '--ru--', flush=True)
    print(Fore.GREEN + translate.text, flush=True)
    texts.append(result)
    texts.append(translate.text)


def try_save_image(image):
    try:
        print('try_save_image', flush=True)
        cropped_image = image.crop((250, 770, 1600, 1000))
        translate_image(cropped_image)
    except Exception as e:
        print('Ошибка при сохранении изображения:', e)

def screen_push():
    last_clipboard_image = ImageGrab.grabclipboard()
    while True:
        print('thread 2', flush=True)
        clipboard_image = ImageGrab.grabclipboard()
        if clipboard_image is not None and clipboard_image != last_clipboard_image:
            try_save_image(clipboard_image)
            last_clipboard_image = clipboard_image
        sleep(1)

thread = Thread(target=screen_push)
thread.daemon = True
thread.start()

app.run( host = "127.0.0.1", port = 5000, debug=True, threaded=True)