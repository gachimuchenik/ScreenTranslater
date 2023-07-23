#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path
import shutil
import sys
import os
import time
import numpy as np
import cv2
import functools

log = logging.getLogger()

def log_and_calc(func):
    @functools.wraps(func)
    def impl(self, *args, **kwargs):
        log.info('{} Start'.format(func.__name__))
        log.debug('{} Args={}'.format(func.__name__, *args))
        start = time.time()
        result = func(self, *args, **kwargs)
        end = time.time()
        log.info('{} Complete in {}ms'.format(
            func.__name__, int((end - start) * 1000)))
        return result
    return impl

def try_delete(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass

def try_rename(from_path, to_path):
    try:
        shutil.move(from_path, to_path)
    except FileNotFoundError:
        pass

def prepare_logger(config):
    if not config.empty_log_on_start or not config.log_path:
        return

    if config.logs_count == 0:
        shutil.rmtree(config.log_path)
    else:
        try:
            for i in range(config.logs_count, -1, -1):
                if i == config.logs_count:
                    try_delete(config.log_path + f'.{str(i)}')
                elif i == 0:
                    try_rename(config.log_path, config.log_path + f'.{str(i+1)}')
                else:
                    try_rename(config.log_path + f'.{str(i)}', config.log_path + f'.{str(i+1)}')
        except PermissionError:
            shutil.rmtree(config.log_path)

    Path(config.log_path).mkdir(parents=True, exist_ok=True)
    open(os.path.join(config.log_path, 'log.log'), 'w').close()

def make_logger(config):
    prepare_logger(config)
    log_level = logging.getLevelName(config.log_level)
    log.setLevel(log_level)
    fmt = '%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(funcName)s:%(lineno)d: %(message)s'
    datefmt='%d.%m.%YT%H:%M:%S'
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    if len(config.log_path) == 0:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(fmt=formatter)
        handler.setLevel(log_level)
        log.addHandler(handler)
    else:
        print(f"log path: {os.path.join(config.log_path, 'log.log')}")
        handler = logging.FileHandler(os.path.join(config.log_path, 'log.log'), 'a')
        handler.setFormatter(fmt=formatter)
        handler.setLevel(log_level)

        err_handler = logging.StreamHandler()
        err_handler.setFormatter(fmt=formatter)
        err_handler.setLevel(logging.ERROR)

        log.addHandler(err_handler)
        log.addHandler(handler)
