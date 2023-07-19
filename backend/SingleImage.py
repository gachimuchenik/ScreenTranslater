#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Translator import Translator
import sys
import argparse
import logging
from PIL import Image
from time import sleep
from Config import Config

from utils import make_logger

log = None


def getParameters():
    parser = argparse.ArgumentParser(prog='Translate single image')

    parser.add_argument('input')
    parser.add_argument('-c', '--config-path', default = 'config.ini')

    args = parser.parse_args()
    config = Config(args.config_path)

    return (config, args.input)


def main():
    (config, input_image) = getParameters()
    log = make_logger(config)
    log.info('==========Started==========\ninput_image={}, config={}'.format(input_image, config.to_dict()))

    translator = Translator(log, config)

    image = Image.open(input_image)
    translator.push_image(image)
    while translator.getCounter() == 0:
        sleep(0.1)
    log.info('result={}'.format(translator.getText()))

    translator.stop()


if __name__ == '__main__':
    main()
