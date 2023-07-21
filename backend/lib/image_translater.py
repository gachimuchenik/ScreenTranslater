#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import functools
import csv

import pytesseract
from googletrans import Translator as GoogleTranslator
from lib.area_pattern_analyzer import AreaPatternAnalyzer


class ImageTranslater(object):
    def log_and_calc(func):
        @functools.wraps(func)
        def impl(self, *args, **kwargs):
            self._log.info('{} Start'.format(func.__name__))
            self._log.debug('{} Args={}'.format(func.__name__, *args))
            start = time.time()
            result = func(self, *args, **kwargs)
            end = time.time()
            self._log.info('{} Complete in {}ms'.format(
                func.__name__, int((end - start) * 1000)))
            return result
        return impl

    def __init__(self, logger, config):
        self._translator = GoogleTranslator()
        self._config = config
        self._log = logger
        self._log.info('Created ImageTranslater')

    def call_method(self, name, *args):
        return getattr(self, name)(*args)

    def run_pipeline(self, data):
        for node in self._config.transform_pipeline:
            data = self.call_method(f'_{node}', data)
        return data

    @log_and_calc
    def process_data(self, data):
        try:
            return self.run_pipeline(data)
        except Exception as e:
            self._log.exception('Accured exception: {}'.format(e))
            return None

    # in: image
    # out: text
    @log_and_calc
    def _recognize_text(self, image):
        """ Find text in image using tesseract
        :param image: input image
        :return: founded text
        """ 
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        input_text = pytesseract.image_to_string(
            image, config=self._config.tesseract_custom_conf, output_type='string')
        input_text = input_text.replace('\n', ' ')
        return input_text

    # in: image
    # out: text
    @log_and_calc
    def _recognize_text_from_tesseract_data(self, image):
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        data_csv = pytesseract.image_to_data(image, config='--psm 3', output_type='string')
        data_csv_lines = data_csv.splitlines()
        csv_reader = csv.reader(data_csv_lines, delimiter='\t')
        csv_reader.__next__() # skip head row
        input_text = ''
        for row in csv_reader:
            confidence = float(row[10])
            text = row[11]
            if confidence > 80:
                input_text += text + ' '
        input_text = input_text.replace('| ', 'I ')
        return input_text

    @log_and_calc
    def _translate_text(self, text):
        """ Translate text
        :param text: input text
        :return: translated text
        """ 
        translated = self._translator.translate(text, dest='ru')
        result = {'en': text, 'ru': translated.text}
        return result

    @log_and_calc
    def _crop_image(self, image):
        """ Crop area from image
        :param image: input image
        :return: cropped image
        """ 
        result = image.crop(self._config.crop_coordinates)
        return result

    @log_and_calc
    def _grayscale_image(self, image):
        """ Grayscale image
        :param image: input image
        :return: grayscaled image
        """ 
        result = image.convert('L').point(
            lambda x: 255 if x > self._config.grayscale_threshold else 0).convert('RGB')
        return result

    @log_and_calc
    def _pattern_analysis(self, image):
        test = AreaPatternAnalyzer(self._config)
        self._log.info(test.pattern_analysis(image))
        return image
