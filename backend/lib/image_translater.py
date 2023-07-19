#!/usr/bin/python3
# -*- coding: utf-8 -*-

from googletrans import Translator as GoogleTranslator
import pytesseract

import time

class ImageTranslater(object):
    def __init__(self, logger, config):
        self._custom_conf = r'--psm 11'
        self._translator = GoogleTranslator()
        self._config = config
        self._log = logger
    
    def process_image(self, image):
        result = None
        try:
            start = time.time()
            result = self.translate_image(self.to_grayscale_image(self.crop_image(image)))
            end = time.time()
            self._log.info(f'translated: {result}, elapsed: {int((end - start) * 1000)}ms')
        except Exception as e:
                self._log.error('Accured exception on translate image: {}'.format(e))
        return result

    def translate_image(self, image):
        
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        result = pytesseract.image_to_string(
            image, config=self._custom_conf, output_type='string')
        result = result.replace('\n', ' ')
        translate = self._translator.translate(result, dest='ru')
        self._log.info('--en--\n{}\n--ru--\n{}'.format(result, translate.text))
        
        
        return result

    def crop_image(self, image):
        return image.crop(self._config.coordinates)

    def to_grayscale_image(self, image):
        grayscale_threshold = 200
        return image.convert('L').point(lambda x: 255 if x > grayscale_threshold else 0).convert('RGB')
            