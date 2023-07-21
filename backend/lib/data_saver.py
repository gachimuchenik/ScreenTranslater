#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path
import os

import PIL
import numpy
import cv2

def precreate_folders(path):
    folder_path = os.path.dirname(path)
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def save_PIL(image, path):
    precreate_folders(path)
    image.save(path)

def save_numpy(image, path):
    precreate_folders(path)
    cv2.imwrite(path, image)

def save_image(image, path):
    if type(image) == PIL.Image.Image:
        save_PIL(image, path)
    if type(image) == numpy.ndarray:
        save_numpy(image, path)