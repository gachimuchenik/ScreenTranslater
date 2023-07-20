#!/usr/bin/python3
# -*- coding: utf-8 -*-

from time import sleep
from threading import Thread, Lock


class Processor(object):
    def __init__(self, logger, config, data_getter, data_processor):
        self._log = logger
        self._inputData = []
        self._outputData = []
        self._is_running = True
        self._data_getter = data_getter
        self._data_processor = data_processor
        self._dataLock = Lock()
        self._reader = Thread(target=self.input_routine)
        self._writer = Thread(target=self.processing_routine)
        self._reader.start()
        self._writer.start()

    def stop(self):
        self._is_running = False
        self._reader.join()
        self._writer.join()

    def processing_routine(self):
        self._counter = 0
        while self._is_running:
            data = None
            with self._dataLock:
                if len(self._inputData) != 0:
                    data = self._inputData.pop(0)
                    self._log.info('New data getted in processing_routine')
            if data:
                text = self._data_processor.process_data(data)
                if text:
                    self._outputData.append(text)
                self._counter += 1
            sleep(0.1)

    def input_routine(self):
        while self._is_running:
            data = None
            try:
                data = self._data_getter.get_data()
            except Exception as e:
                self._log.error('Accured exception: {}'.format(e))
            if data:
                self._inputData.append(data)
                self._log.info('New data getted from data getter')
            sleep(0.1)

    def get_processed_data(self):
        if len(self._outputData) == 0:
            return ""
        return self._outputData.pop(0)

    def push_data(self, data):
        # test purpuses only
        with self._dataLock:
            self._inputData.append(data)

    def get_counter(self):
        return self._counter
