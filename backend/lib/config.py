#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser


class Config(object):
    def __init__(self, path):
        config = configparser.ConfigParser()
        config.read(path)

        # Tesseract config
        self.tesseract_path = config.get('Tesseract', 'tesseract_path')
        self.tesseract_custom_conf = config.get(
            'Tesseract', 'tesseract_custom_conf')

        # Preprocessing config
        self.coordinates = [int(x) for x in config.get(
            'Preprocessing', 'coordinates').split(',')]
        self.grayscale_threshold = config.getint(
            'Preprocessing', 'grayscale_threshold')

        # httpserver config
        self.host = config.get('Network', 'host')
        self.port = config.getint('Network', 'port')

        # system config
        self.log_path = config.get('System', 'log_path')
        self.empty_log_on_start = config.getboolean(
            'System', 'empty_log_on_start')

    def to_dict(self):
        d = {}
        for attr, value in self.__dict__.items():
            d[attr] = value
        return d
