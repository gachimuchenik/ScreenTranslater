#!/usr/bin/python3

from colorama import Fore
from googletrans import Translator
from PIL import ImageGrab
import pytesseract
from threading import Thread
from time import sleep

class Translator(object):
    def __init__(self, tesseract_path='heuasodjaosdj'):
        self._tesseract_path = tesseract_path
        self._texts = []
        self._custom_conf = r'--psm 11'
        self._thread = Thread(target=self.screen_push)
        self._thread.daemon = True
        self._thread.start()
        self._is_running = True

    def stop(self):
        self._is_running = False
        self._thread.join()

    def translate_image(self, image):
        global texts
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        result = pytesseract.image_to_string(
            image, config=self._custom_conf, output_type='string')
        result = result.replace('\n', ' ')
        print(Fore.RED + '--en--', flush=True)
        print(Fore.RED + result, flush=True)
        translate = self._translator.translate(result, dest='ru')
        print(Fore.GREEN + '--ru--', flush=True)
        print(Fore.GREEN + translate.text, flush=True)
        texts.append(result)
        texts.append(translate.text)


    def try_save_image(self, image):
        try:
            print('try_save_image', flush=True)
            cropped_image = image.crop((250, 770, 1600, 1000))
            self.translate_image(cropped_image)
        except Exception as e:
            print('Ошибка при сохранении изображения:', e)


    def screen_push(self):
        last_clipboard_image = ImageGrab.grabclipboard()
        while self._is_running:
            print('thread 2', flush=True)
            clipboard_image = ImageGrab.grabclipboard()
            if clipboard_image is not None and clipboard_image != last_clipboard_image:
                self.try_save_image(clipboard_image)
                last_clipboard_image = clipboard_image
            sleep(1)