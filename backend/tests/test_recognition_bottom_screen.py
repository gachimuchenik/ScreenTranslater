import pytest
import logging
import os
from difflib import SequenceMatcher

import cv2

from lib.config import Config
from lib.image_translater import ImageTranslater

logger = logging.getLogger()

def readfile(path):
    with open(path, 'r') as f:
        return f.read()

def test_on_prepared_data():
    skip = ['7']
    current_folder = os.path.dirname(__file__) 
    config = Config(current_folder, '../config.ini')
    config.coordinates = (250,770,1600,1000)
    translater = ImageTranslater(logger, config)
    images_folder = os.path.join(current_folder, './data/images')
    texts_folder = os.path.join(current_folder, './data/results')

    for entry in os.scandir(images_folder):
        image_name = entry.name
        name = os.path.splitext(image_name)[0]
        if name in skip:
            continue

        text_path = os.path.join(texts_folder, name)
        image_path = os.path.join(images_folder, image_name)

        text = readfile(text_path)
        image = cv2.imread(image_path)

        result = translater.process_data(image)

        print ('accuracy={}'.format(SequenceMatcher(None, result['en'], text).ratio()))
        assert SequenceMatcher(None, result['en'], text).ratio() > 0.75, "Lines not equal enough"