#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
from time import sleep
import logging

import cv2

from lib.config import Config
from lib.utils import make_logger
from lib.creator import make_image_processor

log = None


def getParameters():
    parser = argparse.ArgumentParser(prog='Translate single image')

    parser.add_argument('input')
    parser.add_argument('-c', '--config-path', default='config.ini')

    args = parser.parse_args()
    config = Config(os.path.dirname(__file__), args.config_path)

    return (config, args.input)


def main():
    (config, input_image) = getParameters()
    log = make_logger(config)
    log = logging.getLogger("main")
    log.info('==========Started==========\ninput_image={}, config={}'.format(
        input_image, config.to_dict()))

    config.data_getter_type = 'clipboard'
    translator = make_image_processor(config)

    image = cv2.imread(input_image)
    translator.push_data(image)
    while translator.get_counter() == 0:
        sleep(0.1)
    result = translator.get_processed_data()
    
    print(result['original_text'])
    print(result['translated_text'])

    translator.stop()


if __name__ == '__main__':
    main()
