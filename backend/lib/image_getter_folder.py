#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import Image
import os


class ImageGetterFolder(object):
    def __init__(self, log, path):
        self._last_image = None
        self._log = log
        self._path = path
        self._done = False
        self._log.info('Created ImageGetterFolder')
        self._folder_files = self.image_generator()
    
    def image_generator(self):
        for entry in os.scandir(self._path):
            if entry.is_file():
                self._log.info(f'readed file: {entry.name}')
                yield Image.open(entry.path)
        self._log.info('Folder readed complete')
        print('Folder readed complete')
        self._done = True
        yield None

    def get_data(self):
        if self._done:
            return None
        return next(self._folder_files)
