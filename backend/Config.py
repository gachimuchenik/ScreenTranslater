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
        self.log_path = config.get('System', 'log_path')
        self.empty_log_on_start = config.getboolean('System', 'empty_log_on_start')
    
    def to_dict(self):
        d={}
        for attr, value in self.__dict__.items():
            d[attr] = value
        return d
