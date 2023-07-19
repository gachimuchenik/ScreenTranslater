#!/usr/bin/python3
# -*- coding: utf-8 -*-

from threading import Thread, Lock
from time import sleep

from image_getter import ImageGetter
from image_translater import ImageTranslater


class Translator(object):
    def __init__(self, logger, config):
        self._inputData = []
        self._outputData = []

        self._is_running = True

        self._dataLock = Lock()
        self._reader = Thread(target=self.output_routine)
        self._writer = Thread(target=self.input_routine)

        self._reader.start()
        self._writer.start()

        self._image_getter = ImageGetter()
        self._image_translater = ImageTranslater(logger, config)

    def stop(self):
        self._is_running = False
        self._reader.join()
        self._writer.join()

    def input_routine(self):
        self._counter = 0
        while self._is_running:
            image = None
            with self._dataLock:
                if len(self._inputData) != 0:
                    image = self._inputData.pop(0)
            if image:
                text = self._image_translater.translate_image(image)
                if text:
                    self._outputData.append(text)
                self._counter += 1
            sleep(0.1)

    def output_routine(self):
        while self._is_running:
            image = None
            try:
                image = self._image_getter.get_last_image()
            except Exception as e:
                self._log.error('Accured exception: {}'.format(e))
            if image:
                self._inputData.append(image)
            sleep(0.1)

    def getText(self):
        if len(self._outputData) == 0:
            return ""
        return self._outputData.pop(0)

    def push_image(self, image):
        # test purpuses only
        with self._dataLock:
            self._inputData.append(image)

    def getCounter(self):
        return self._counter
