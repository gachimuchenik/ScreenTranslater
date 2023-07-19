#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Translator import Translator
import sys
import argparse
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger()


def getParameters():
    parser = argparse.ArgumentParser(
        prog='Translate single image')
    parser.add_argument('input')
    parser.add_argument('-p', '--tesseract_path', default='C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    parser.add_argument('--x1', default=250)
    parser.add_argument('--y1', default=770)
    parser.add_argument('--x2', default=1600)
    parser.add_argument('--y2', default=1000)
    args = parser.parse_args()
    log.info('running with: args={}'.format(
        args))
    return args


def main():
    args = getParameters()
    translator = Translator(log, args)

    with open(args.input, 'rb') as f:
        image = f.read()
        translator.push_image(image)

    translator.stop()


if __name__ == '__main__':
    main()
