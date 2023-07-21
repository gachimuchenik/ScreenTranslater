#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import functools
import csv
import os
import logging

import pytesseract
# import pkg_resources
# from symspellpy import SymSpell, Verbosity
from spellchecker import SpellChecker
from googletrans import Translator as GoogleTranslator
import cv2
import numpy as np
from lib.area_pattern_analyzer import AreaPatternAnalyzer
from lib.data_saver import save_image
from lib.area_pattern_analyzer import AreaPatternAnalyzer

log = logging.getLogger(__name__)

class ImageTranslater(object):
    def log_and_calc(func):
        @functools.wraps(func)
        def impl(self, *args, **kwargs):
            log.info('{} Start'.format(func.__name__))
            log.debug('{} Args={}'.format(func.__name__, *args))
            start = time.time()
            result = func(self, *args, **kwargs)
            end = time.time()
            log.info('{} Complete in {}ms'.format(
                func.__name__, int((end - start) * 1000)))
            return result
        return impl

    def __init__(self, config):
        self._translator = GoogleTranslator()
        self._config = config
        log.info('Created ImageTranslater')
        self._id = 0
        self._spellcheck = SpellChecker(distance=1)  
        self._pattern_analyser = AreaPatternAnalyzer(config)
        # self._spellcheck.word_frequency.load_text_file(os.path.dirname(__file__), "frequency_dictionary_en_82_765.txt")
        # self._sym_spell = SymSpell(max_dictionary_edit_distance=1, prefix_length=4)
        # dictionary_path = os.path.join(os.path.dirname(__file__), "frequency_dictionary_en_82_765.txt")
        # self._sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)


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
            log.exception('Accured exception: {}'.format(e))
        finally:
            log.info(f'{self._id} Result = "{result}"')
            self._id += 1
        return result

    @log_and_calc
    def _crunch_after_recognize(self, text):
        text = text.replace(' | ', ' I ')
        text = text.replace('  ', ' ')
        text = text.replace('(A)', '')
        return text
    
    @log_and_calc
    def _autocorrect(self, text):
        # return text
        splitted_text = self._spellcheck.split_words(text)
        log.error(splitted_text)
        result_text = []
        for word in splitted_text:
            try:
                suggested = self._spellcheck.correction(word)
                if not suggested or suggested == word:
                    continue
                text.replace(word, suggested)
                log.error('replaced {} -> {}'.format(word, suggested))
            except ValueError:
                result_text.append(word)
        return text
        
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
        data_csv = pytesseract.image_to_data(image, config=self._config.tesseract_custom_conf, output_type='string')
        data_csv_lines = data_csv.splitlines()
        csv_reader = csv.reader(data_csv_lines, delimiter='\t')
        csv_reader.__next__() # skip head row
        input_text = ''
        for row in csv_reader:
            confidence = float(row[10])
            text = row[11]
            if confidence > 15:
                input_text += text + ' '
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
            log.exception(e)
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
        return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 101, -100)
        # return cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)[1]
        

    @log_and_calc
    def _pattern_analysis(self, image):
        test = AreaPatternAnalyzer(self._config)
        log.info(test.pattern_analysis(image))
        return image

    @log_and_calc
    def _get_areas(self, image):
        return self._pattern_analyser.get_boxes(image)

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

    @log_and_calc
    def _resize(self, image):
        scale_percent = 50 # percent of original size
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        
        # resize image
        return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)