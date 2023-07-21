#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path
import shutil
import sys
import os

from lib.processor import Processor
from lib.image_getter_clipboard import ImageGetterClipboard
from lib.image_getter_folder import ImageGetterFolder
from lib.image_translater import ImageTranslater
from lib.data_saver import precreate_folders

def try_delete(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass

def try_rename(from_path, to_path):
    try:
        os.rename(from_path, to_path)
    except FileNotFoundError:
        pass

def prepare_logger(config):
    if not config.empty_log_on_start or not config.log_path:
        return

    try:
        for i in range(config.logs_count, -1, -1):
            if i == config.logs_count:
                try_delete(os.path.join(config.log_path, f'.{str(i)}'))
            elif i == 0:
                try_rename(config.log_path, config.log_path + f'.{str(i+1)}')
            else:
                try_rename(config.log_path + f'.{str(i)}', config.log_path + f'.{str(i+1)}')
    except PermissionError:
        shutil.rmtree(config.log_path)

    Path(config.log_path).mkdir(parents=True, exist_ok=True)

def make_logger(config):
    prepare_logger(config)
    log_level = logging.getLevelName(config.log_level)
    if len(config.log_path) == 0:
        logging.basicConfig(stream=sys.stdout, level=log_level,
                            format='%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(funcName)s:%(lineno)d: %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    else:
        logging.basicConfig(filename=os.path.join(config.log_path, 'log.log'), level=log_level,
                            format='%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(funcName)s:%(lineno)d: %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    return logging.getLogger()

def make_image_getter(log, config):
    if config.data_getter_type == 'clipboard':
        return ImageGetterClipboard(log, config.use_fake_image_getter)
    elif config.data_getter_type == 'folder':
        return ImageGetterFolder(log, config.getter_folder_path)
    raise RuntimeError(f'Unknown Data Getter type: {config.data_getter_type}')

def make_image_processor(config, log):
    return Processor(log, config, make_image_getter(log, config), ImageTranslater(log, config))
