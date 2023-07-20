#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import ImageGrab


class ImageGetter(object):
    def __init__(self, log, mocked=False):
        self._last_image = None
        self._mocked = mocked
        self._log = log

    def get_data(self):
        if self._mocked:
            return None
        clipboard_image = ImageGrab.grabclipboard()
        if clipboard_image != None and self._last_image != clipboard_image:
            self._log.debug('New image: {}'.format(clipboard_image))
            self._last_image = clipboard_image
            return self._last_image
        else:
            return None
