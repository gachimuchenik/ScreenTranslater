#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

import pytesseract
from googletrans import Translator as GoogleTranslator


class ImageTranslater(object):
    def __init__(self, logger, config):
        self._translator = GoogleTranslator()
        self._config = config
        self._log = logger
        self._log.info('Created ImageTranslater')

    def process_data(self, image):
        self._log.info('Start')
        result = None
        try:
            start = time.time()
            result = self._translate_image(
                self._to_grayscale_image(self._crop_image(image)))
            end = time.time()
            self._log.info(
                f'Image processed: {result}, elapsed: {int((end - start) * 1000)}ms')
        except Exception as e:
            self._log.exception(
                'Accured exception: {}'.format(e))
        self._log.info('Complete')
        return result

    def _translate_image(self, image):
        self._log.info('Start')
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        input_text = pytesseract.image_to_string(
            image, config=self._config.tesseract_custom_conf, output_type='string')
        input_text = input_text.replace('\n', ' ')
        self._log.info('input_text={}'.format(input_text))
        translated = self._translator.translate(input_text, dest='ru')
        result = {'en': input_text, 'ru': translated.text}
        self._log.info('Complete')
        return result

    def _crop_image(self, image):
        self._log.info('Start')
        result = image.crop(self._config.coordinates)
        self._log.info('Complete')
        return result

    def _to_grayscale_image(self, image):
        self._log.info('Start')
        result = image.convert('L').point(
            lambda x: 255 if x > self._config.grayscale_threshold else 0).convert('RGB')
        self._log.info('Complete')
        return result
