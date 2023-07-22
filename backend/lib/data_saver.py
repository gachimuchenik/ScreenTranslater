#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path
import os
import logging

import PIL
import numpy
import cv2

log = logging.getLogger(__name__)

def precreate_folders(path):
    folder_path = os.path.dirname(path)
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def save_PIL(image, path):
    precreate_folders(path)
    image.save(path)

def save_numpy(image, path):
    precreate_folders(path)
    cv2.imwrite(path, image)

def save_dict(data, path, name):
    if 'image' in data:
        save_data(data['image'], path, name)
    num = 0
    if 'images' in data:
        for image in data['images']:
            save_data(image, path, f'{name}_{num}')
            num += 1

def save_data(data, path, name):
    log.debug(f'Start save data {name}, type={type(data)}')
    if type(data) == PIL.Image.Image:
        save_PIL(data, os.path.join(path, name + '.png'))
    if type(data) == numpy.ndarray:
        save_numpy(data, os.path.join(path, name + '.png'))
    if type(data) == dict:
        save_dict(data, path, name)

