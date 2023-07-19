#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

def make_logger(config):
    if config.empty_log_on_start and config.log_path:
        open(config.log_path, 'w').close()
    if not config.log_path:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    else:
        logging.basicConfig(filename=config.log_path, level=logging.INFO, format='%(levelname)s %(asctime)s %(filename)s:%(lineno)d: %(message)s', datefmt='%d.%m.%YT%H:%M:%S')
    return logging.getLogger()
    