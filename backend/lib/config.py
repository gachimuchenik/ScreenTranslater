#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import platform


class Config(object):
    def __init__(self, root_path, path):
        config = configparser.ConfigParser()
        print(f'get config from {os.path.join(root_path, path)}')
        config.read(os.path.join(root_path, path))

        # Tesseract config
        self.tesseract_path = config.get('Tesseract', 'tesseract_path')
        if len(self.tesseract_path) == 0:
            self.tesseract_path = 'tesseract'
            if platform == 'Windows':
                self.tesseract_path += '.exe'
                
        self.tesseract_custom_conf = config.get(
            'Tesseract', 'tesseract_custom_conf')
        
        # Data processor config
        self.max_buffer_length = max(config.getint('DataProcessor', 'max_buffer_length'), 1)

        # Preprocessing config
        self.crop_coordinates = [int(x) for x in config.get(
            'ImageProcessing', 'crop_coordinates').split(',')]
        self.grayscale_threshold = config.getint(
            'ImageProcessing', 'grayscale_threshold')
        self.transform_pipeline = config.get('ImageProcessing', 'pipeline').replace(' ', '').split(',')

        # httpserver config
        self.host = config.get('Network', 'host')
        self.port = config.getint('Network', 'port')

        # system config
        self.log_path = config.get('System', 'log_path')
        if len(self.log_path) != 0:
            os.path.join(root_path, self.log_path)
        self.log_level = config.get('System', 'log_level')
        self.empty_log_on_start = config.getboolean(
            'System', 'empty_log_on_start')
        self.log_images = config.getboolean('System', 'log_images')

        # data getter
        self.data_getter_type = config.get('DataGetter', 'type') # values: folder, clipboard
        self.use_fake_image_getter = config.getboolean('ClipboardGetter', 'use_fake_image_getter')
        self.getter_folder_path = os.path.join(root_path, config.get('FolderGetter', 'folder_path'))

    def to_dict(self):
        d = {}
        for attr, value in self.__dict__.items():
            d[attr] = value
        return d
