#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import argparse
from time import sleep

from PIL import Image

from lib.config import Config
from lib.utils import make_logger, make_image_processor

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
    log.info('==========Started==========\ninput_image={}, config={}'.format(
        input_image, config.to_dict()))

    translator = make_image_processor(config, log)

    image = Image.open(input_image)
    translator.push_data(image)
    while translator.get_counter() == 0:
        sleep(0.1)
    result = translator.get_processed_data()
    log.info('result="{}"'.format(result))
    print('result="{}"'.format(result))

    translator.stop()


if __name__ == '__main__':
    main()
