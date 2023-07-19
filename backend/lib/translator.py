#!/usr/bin/python3
# -*- coding: utf-8 -*-

from colorama import Fore
from googletrans import Translator as GoogleTranslator
import pytesseract
from threading import Thread, Lock
from time import sleep
import time

from image_getter import ImageGetter


class Translator(object):
    def __init__(self, logger, config):
        # config:
        # tesseract_path = 'path to tesseract.exe', str
        # x1, x2, y1, y2: text coorinates, int
        self._config = config
        self._log = logger
        self._inputImage = []
        self._outputText = []
        self._custom_conf = r'--psm 11'
        self._translator = GoogleTranslator()
        self._is_running = True
        self._reader = Thread(target=self.get_image_routine)
        self._writer = Thread(target=self.translator_routine)
        self._imageLock = Lock()
        self._reader.start()
        self._writer.start()
        self._image_getter = ImageGetter()

    def stop(self):
        self._is_running = False
        self._reader.join()
        self._writer.join()

    def translator_routine(self):
        self._counter = 0
        while self._is_running:
            image = None
            with self._imageLock:
                if len(self._inputImage) != 0:
                    image = self._inputImage.pop(0)
            if image:
                try:
                    self.translate_image(
                        self.to_grayscale_image(self.crop_image(image)))
                except Exception as e:
                    self._log.error(
                        'Accured exception on translate image: {}'.format(e))
                finally:
                    self._counter += 1
                    image = None
            sleep(0.1)

    def translate_image(self, image):
        start = time.time()
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        result = pytesseract.image_to_string(
            image, config=self._custom_conf, output_type='string')
        result = result.replace('\n', ' ')
        translate = self._translator.translate(result, dest='ru')
        self._log.info('--en--\n{}\n--ru--\n{}'.format(result, translate.text))
        self._outputText.append({'en': result, 'ru': translate.text})
        end = time.time()
        self._log.error(f'{round(end - start, 2)} second')

    def crop_image(self, image):
        return image.crop(self._config.coordinates)

    def to_grayscale_image(self, image):
        grayscale_threshold = 220
        return image.convert('L').point(lambda x: 255 if x > grayscale_threshold else 0).convert('RGB')

    def get_image_routine(self):
        while self._is_running:
            image = None
            try:
                image = self._image_getter.get_last_image()
            except Exception as e:
                self._log.error('Accured exception: {}'.format(e))
            if image:
                self._inputImage.append(image)
            sleep(0.1)

    def getText(self):
        if len(self._outputText) == 0:
            return ""
        return self._outputText.pop(0)

    def push_image(self, image):
        # test purpuses only
        with self._imageLock:
            self._inputImage.append(image)

    def getCounter(self):
        return self._counter
