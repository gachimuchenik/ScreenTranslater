#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os


class Config(object):
    def __init__(self, root_path, path):
        config = configparser.ConfigParser()
        config.read(os.path.join(root_path, path))

        # Tesseract config
        self.tesseract_path = config.get('Tesseract', 'tesseract_path')
        self.tesseract_custom_conf = config.get(
            'Tesseract', 'tesseract_custom_conf')
        
        # Data processor config
        self.max_buffer_length = max(config.getint('DataProcessor', 'max_buffer_length'), 1)

        # Preprocessing config
        self.coordinates = [int(x) for x in config.get(
            'Preprocessing', 'coordinates').split(',')]
        self.grayscale_threshold = config.getint(
            'Preprocessing', 'grayscale_threshold')

        # httpserver config
        self.host = config.get('Network', 'host')
        self.port = config.getint('Network', 'port')

        # system config
        self.log_path = os.path.join(root_path, config.get('System', 'log_path'))
        self.log_level = config.get('System', 'log_level')
        self.empty_log_on_start = config.getboolean(
            'System', 'empty_log_on_start')

        # data getter
        self.use_fake_image_getter = config.getboolean('DataGetter', 'use_fake_image_getter')

    def to_dict(self):
        d = {}
        for attr, value in self.__dict__.items():
            d[attr] = value
        return d
