import pytest
import logging
import os
from difflib import SequenceMatcher

import cv2

from lib.config import Config
from lib.image_translater import ImageTranslater

def readfile(path):
    result = []
    with open(path, 'r') as f:
        for line in f:
            result.append(line)
    return result

def test_on_prepared_data():
    skip = ['7']
    current_folder = os.path.dirname(__file__) 
    config = Config(current_folder, '../config.ini')
    config.transform_pipeline = config.transform_pipeline[0:-1]
    translater = ImageTranslater(config)
    images_folder = os.path.join(current_folder, './data/images')
    texts_folder = os.path.join(current_folder, './data/results')

    for entry in os.scandir(images_folder):
        image_name = entry.name
        name = os.path.splitext(image_name)[0]
        if name in skip:
            continue
        print(f'testing {name}')

        text_path = os.path.join(texts_folder, name)
        image_path = os.path.join(images_folder, image_name)

        texts = readfile(text_path)
        image = cv2.imread(image_path)

        result = translater.process_data(image)
        recognized = result['original_text']

        recognized_counter = 0
        for recognized_text in recognized:
            max_match = 0
            best_guess = ''

            print(f'--{recognized_text}')
            for text in texts:
                print(f'----{text}')
                accuracy = SequenceMatcher(None, recognized_text, text).ratio()
                if accuracy > max_match:
                    max_match = accuracy
                    best_guess = text
                print(f'----accuracy: {accuracy}')
            if max_match > 0.85:
                recognized_counter += 1
            print('\n')

        assert recognized_counter == len(texts)