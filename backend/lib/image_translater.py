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
from lib.data_saver import save_data
from lib.area_pattern_analyzer import AreaPatternAnalyzer
from lib.utils import log_and_calc
import lib.preprocessing as preprocessing

log = logging.getLogger(__name__)

class ImageTranslater(object):
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
        step = 0
        for node in self._config.transform_pipeline:
            step += 1
            data = self.call_method(f'_{node}', data)
            if not self._config.log_images:
                continue
            save_data(data, os.path.join(self._config.log_path, str(self._id)), f'step{step}_' + node)
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
        if type(text) == dict:
            return self._run_multiple_data(self._crunch_after_recognize, text, 'original_text', 'original_text')
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
        if type(image) == dict:
            return self._run_multiple_data(self._recognize_text, image, 'images', 'original_text')
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        input_text = pytesseract.image_to_string(
            image, config=self._config.tesseract_custom_conf, output_type='string')
        input_text = input_text.replace('\n', ' ')
        return input_text

    # in: image
    # out: text
    @log_and_calc
    def _recognize_text_from_tesseract_data(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._recognize_text_from_tesseract_data, image, 'images', 'original_text')
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        data_csv = pytesseract.image_to_data(image, config=self._config.tesseract_custom_conf, output_type='string')
        data_csv_lines = data_csv.splitlines()
        csv_reader = csv.reader(data_csv_lines, delimiter='\t')
        csv_reader.__next__() # skip head row
        input_text = ''
        log.info(data_csv_lines)
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
        if type(text) == dict:
            return self._run_multiple_data(self._translate_text, text, 'original_text', 'translated_text')
        translated_text = None
        try:
            translated = self._translator.translate(text, dest='ru')
            translated_text = translated.text
        except Exception as e:
            log.exception(e)
        return translated_text
    
    @log_and_calc
    def _run_multiple_data(self, function, data, input_field='images', output_field='images'):
        result = []
        for obj in data[input_field]:
            obj = function(obj)
            if type(obj) == str:
                log.info(f'{function.__name__} result {obj}')
            result.append(obj)
        data[output_field] = result
        return data

    @log_and_calc
    def _pattern_analysis(self, image):
        test = AreaPatternAnalyzer(self._config)
        log.info(test.pattern_analysis(image))
        return image
    
    @log_and_calc
    def _get_areas(self, image):
        return self._pattern_analyser.get_boxes(image)
    
    @log_and_calc
    def _get_areas_tess(self, image):
        prepared_image = self._grayscale(image)
        prepared_image = self._remove_noise(prepared_image)
        prepared_image = self._gaussian_blur(prepared_image)
        prepared_image = self._adaptive_threshold(prepared_image)
        # prepared_image = self._thinning(prepared_image)
        result = self._pattern_analyser.get_boxes_2(prepared_image)
        for box in result['boxes']:
            cv2.rectangle(prepared_image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        result['image'] = prepared_image
        result['real_image'] = image
        return result
        
    @log_and_calc
    def _print_prepared_image(self, data):
        data['image'] = data['real_image']
        del data['real_image']
        return data
    
    @log_and_calc
    def _crop_fields(self, data):
        image = data['image']
        boxes = data['boxes']
        result = {'boxes': [], 'images': [], 'original_image': image}
        for box in boxes:
            result['boxes'].append(box)
            result['images'].append(preprocessing.crop_image(image, box))
        return result

    @log_and_calc
    def _resize(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._crop_image, image)
        return preprocessing.resize(image)

    @log_and_calc
    def _normalization(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._normalization, image)
        norm_img = np.zeros((image.shape[0], image.shape[1]))
        return cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
    
    @log_and_calc
    def _deskew(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._deskew, image)
        co_ords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(co_ords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    @log_and_calc
    def _thinning(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._thinning, image)
        kernel = np.ones((3,3),np.uint8)
        return cv2.erode(image, kernel, iterations = 1)
    
    @log_and_calc
    def _remove_noise_colored(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._remove_noise, image)
        return cv2.fastNlMeansDenoisingColored(image, None, 15, 10, 21, 7)

    @log_and_calc
    def _remove_noise(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._remove_noise, image)
        # return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 15)
    

    @log_and_calc
    def _threshold(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._threshold, image)
        return preprocessing.threshold(image)


    @log_and_calc
    def _adaptive_threshold(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._adaptive_threshold, image)
        return preprocessing.adaptive_threshold(image)

    @log_and_calc
    def _grayscale(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._grayscale, image)
        return preprocessing.grayscale_image(image)
    
    @log_and_calc
    def _gaussian_blur(self, image):
        if type(image) == dict:
            return self._run_multiple_data(self._gaussian_blur, image)
        return preprocessing.gaussian_blur(image)

    

    