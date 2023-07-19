#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser

class Config(object):
    def __init__(self, path):
        config = configparser.ConfigParser()
        config.read(path)

        self.tesseract_path = config.get('Translator', 'tesseract_path')
        self.coordinates = [int(x) for x in config.get('Translator', 'coordinates').split(',')]
        self.host = config.get('Network', 'host')
        self.port = config.getint('Network', 'port')
