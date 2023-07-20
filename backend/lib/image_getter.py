#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import ImageGrab


class ImageGetter(object):
    def __init__(self):
        self._last_image = None

    def get_data(self):
        clipboard_image = ImageGrab.grabclipboard()
        if clipboard_image != None and self._last_image != clipboard_image:
            self._last_image = clipboard_image

        return self._last_image
