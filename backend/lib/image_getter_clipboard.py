#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PIL import ImageGrab
import cv2
import numpy as np
import logging

log = logging.getLogger(__name__)


class ImageGetterClipboard(object):
    def __init__(self, log, mocked=False):
        self._last_image = None
        self._mocked = mocked
        log.info('Created ImageGetterClipboard')

    def get_data(self):
        if self._mocked:
            return None
        clipboard_image = ImageGrab.grabclipboard()
        if clipboard_image != None and self._last_image != clipboard_image:
            clipboard_image = cv2.cvtColor(np.array(clipboard_image), cv2.COLOR_RGB2BGR)
            log.debug('New image: {}'.format(clipboard_image))
            self._last_image = clipboard_image
            return self._last_image
        else:
            return None
