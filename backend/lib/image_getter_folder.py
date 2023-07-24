#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
import cv2

log = logging.getLogger(__name__)

class ImageGetterFolder(object):
    def __init__(self, path):
        self._last_image = None
        self._path = path
        self._done = False
        log.info('Created ImageGetterFolder')
        self._folder_files = self.image_generator()
    
    def image_generator(self):
        for entry in os.scandir(self._path):
            if entry.is_file():
                log.info(f'readed file: {entry.name}')
                yield cv2.imread(entry.path)
        log.info('Folder readed complete')
        self._done = True
        yield None

    def get_data(self):
        if self._done:
            return None
        return next(self._folder_files)
