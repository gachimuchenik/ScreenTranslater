#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import functools
import csv
import os

import pytesseract
from googletrans import Translator as GoogleTranslator
import cv2
import numpy as np

from lib.data_saver import save_image
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
        self._id = 0

    def call_method(self, name, *args):
        return getattr(self, name)(*args)

    def run_pipeline(self, data):
        for node in self._config.transform_pipeline:
            data = self.call_method(f'_{node}', data)
            if not self._config.log_images:
                continue
            save_image(data, os.path.join(self._config.log_path, str(self._id), node + '.png'))
        return data

    @log_and_calc
    def process_data(self, data):
        result = None
        try:
            result = self.run_pipeline(data)
        except Exception as e:
            self._log.exception('Accured exception: {}'.format(e))
        finally:
            self._log.info(f'{self._id} Result = "{result}"')
            self._id += 1
        return result

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
        # crunch:
        input_text = input_text.replace(' | ', ' I ')
        input_text = input_text.replace('  ', ' ')
        # crunch:
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
        translated_text = None
        try:
            translated = self._translator.translate(text, dest='ru')
            translated_text = translated.text
        except Exception as e:
            self._log.exception(e)
        result = {'en': text, 'ru': translated_text}
        return result

    @log_and_calc
    def _crop_image(self, image):
        """ Crop area from image
        :param image: input image
        :return: cropped image
        """ 
        x1 = self._config.crop_coordinates[0]
        x2 = self._config.crop_coordinates[2]
        y1 = self._config.crop_coordinates[1]
        y2 = self._config.crop_coordinates[3]
        return image[y1:y2, x1:x2]
    
    @log_and_calc
    def _grayscale_image(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @log_and_calc
    def _denoiser(self, image):
        return cv2.medianBlur(image, 3)
    
    @log_and_calc
    def _gaussian_blur(self, image):
        return cv2.GaussianBlur(image, (3,3), 0)
    
    @log_and_calc
    def _bilateral_filter(self, image):
        return cv2.bilateralFilter(image, 3, 75, 75)
    
    @log_and_calc
    def _thresholding(self, image):
        return cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)[1]

    @log_and_calc
    def _pattern_analysis(self, image):
        test = AreaPatternAnalyzer(self._config)
        self._log.info(test.pattern_analysis(image))
        return image

    @log_and_calc
    def _canny(self, image):
        return cv2.Canny(image=image, threshold1=100, threshold2=200) 
    
    @log_and_calc
    def _kmeans(self, image):
        Z = image.reshape((-1,3))
        Z = np.float32(Z)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 4
        ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

        center = np.uint8(center)
        res = center[label.flatten()]
        res2 = res.reshape((image.shape))

        return res2

