#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib.processor import Processor
from lib.image_getter_clipboard import ImageGetterClipboard
from lib.image_getter_folder import ImageGetterFolder
from lib.image_translater import ImageTranslater

def make_image_getter(config):
    if config.data_getter_type == 'clipboard':
        return ImageGetterClipboard(config.use_fake_image_getter)
    elif config.data_getter_type == 'folder':
        return ImageGetterFolder(config.getter_folder_path)
    raise RuntimeError(f'Unknown Data Getter type: {config.data_getter_type}')

def make_image_processor(config):
    return Processor(config, make_image_getter(config), ImageTranslater(config))