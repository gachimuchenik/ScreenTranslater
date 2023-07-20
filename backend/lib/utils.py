#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

from lib.processor import Processor
from lib.image_getter import ImageGetter
from lib.image_translater import ImageTranslater


def make_logger(config):
    if config.empty_log_on_start and config.log_path:
        open(config.log_path, 'w').close()
    log_level = logging.getLevelName(config.log_level)
    if not config.log_path:
        logging.basicConfig(stream=sys.stdout, level=log_level,
                            format='%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(funcName)s:%(lineno)d: %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    else:
        logging.basicConfig(filename=config.log_path, level=log_level,
                            format='%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(funcName)s:%(lineno)d: %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    return logging.getLogger()


def make_image_processor(config, log):
    return Processor(log, config, ImageGetter(log, config.use_fake_image_getter), ImageTranslater(log, config))
