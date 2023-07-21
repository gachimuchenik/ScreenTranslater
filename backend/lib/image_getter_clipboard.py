#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import ImageGrab
from lib.utils import pil_2_cv


class ImageGetterClipboard(object):
    def __init__(self, log, mocked=False):
        self._last_image = None
        self._mocked = mocked
        self._log = log
        self._log.info('Created ImageGetterClipboard')

    def get_data(self):
        if self._mocked:
            return None
        clipboard_image = pil_2_cv(ImageGrab.grabclipboard())
        if clipboard_image != None and self._last_image != clipboard_image:
            self._log.debug('New image: {}'.format(clipboard_image))
            self._last_image = clipboard_image
            return self._last_image
        else:
            return None
