#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

from lib.processor import Processor
from lib.image_getter_clipboard import ImageGetterClipboard
from lib.image_getter_folder import ImageGetterFolder
from lib.image_translater import ImageTranslater


def make_logger(config):
    if config.empty_log_on_start and config.log_path:
        open(config.log_path, 'w').close()
    log_level = logging.getLevelName(config.log_level)
    if len(config.log_path) == 0:
        logging.basicConfig(stream=sys.stdout, level=log_level,
                            format='%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(funcName)s:%(lineno)d: %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    else:
        logging.basicConfig(filename=config.log_path, level=log_level,
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
