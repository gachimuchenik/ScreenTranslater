import pytesseract
import csv
import logging
import os

import cv2
import numpy as np
from imutils.object_detection import non_max_suppression


import time

log = logging.getLogger(__name__)

class AreaPattern(object):
    def __init__(self, name, bounds):
        self.name = name
        self.bounds = bounds
        self._bounds_valids = [False] * len(self.bounds)

    def reset(self):
        for i, bounds_valid in enumerate(self._bounds_valids):
            self._bounds_valids[i] = False

    def get_valid(self):
        return sum(self._bounds_valids) == len(self._bounds_valids)

    def bounds_contains(self, text_bounds):
        for i, bounds in enumerate(self.bounds):
            if bounds[0] <= text_bounds[0] and bounds[1] <= text_bounds[1] and bounds[2] >= text_bounds[2] and bounds[3] >= text_bounds[3]:
                self._bounds_valids[i] = True


class AreaPatternAnalyzer(object):
    def __init__(self, config):
        self._config = config
        
        self._patterns = [
            AreaPattern('gameplay dialog', [
                    (440, 766, 1480, 816), # dialog name
                    (440, 822, 1480, 990), # dialog text
                ]),
            AreaPattern('gameplay phone dialog', [
                    (440, 766, 1480, 816), # dialog name
                    (440, 822, 1480, 990), # dialog text
                    (496,  98, 1572, 148), # phone name
                    (496, 158, 1572, 272), # phone text
                ]),
            AreaPattern('cutscene', [
                    (440, 880, 1480, 1050), # cutscene text
                ]),
        ]
    
    def make_block_bigger(self, box, W, H, perc):
        newBox = np.array([0,0,0,0])
        w = int(((box[2] - box[0]) / 100.0) * perc)
        h = int(((box[3] - box[1]) / 100.0) * perc)
        minVal = min(w, h)
        newBox[0] = max(box[0] - minVal, 0)
        newBox[1] = max(box[1] - minVal, 0)
        newBox[2] = min(box[2] + minVal, W)
        newBox[3] = min(box[3] + minVal, H)
        return newBox

    def combine_boxes(self, box1, box2):
        return (min(box1[0], box2[0]), min(box1[1], box2[1]), max(box1[2], box2[2]), max(box1[3], box2[3]))
    
    def get_real_lines(self, boxes, W, H):
        # join horizontally
        boxes = boxes[np.argsort(boxes[:, 0])]
        for i in range(len(boxes)):
            if boxes[i][0] == -1:
                continue
            for j in range(i+1, len(boxes)):
                if boxes[j][0] == -1:
                    continue 
                if boxes[i][3] < boxes[j][1] or boxes[i][1] > boxes[j][3]: 
                    continue
                icx = ((boxes[i][2] - boxes[i][0]) / 2) + boxes[i][0]
                jcx = ((boxes[j][2] - boxes[j][0]) / 2) + boxes[j][0]
                if icx > jcx:
                    if boxes[i][0] - boxes[j][2] >  W / 10:
                        continue
                if jcx > icx:
                    if boxes[j][0] - boxes[i][2] > W / 10:
                        continue
                boxes[i] = self.combine_boxes(boxes[i], boxes[j])
                boxes[j] = np.array([-1,-1,-1,-1])
        boxes = boxes[~np.all(boxes == -1, axis=1)]
        boxes = np.unique(boxes, axis=0)

        # join vertically
        boxes = boxes[np.argsort(boxes[:, 1])]
        for i in range(len(boxes)):
            if boxes[i][1] == -1:
                continue
            diff = (boxes[i][3] - boxes[i][1]) * 0.8
            for j in range(i+1, len(boxes)):
                if boxes[j][0] == 0:
                    continue
                if boxes[i][2] < boxes[j][0] or boxes[i][0] > boxes[j][2]: 
                    continue
                if boxes[i][3] + diff < boxes[j][1]:
                    continue
                boxes[i] = self.combine_boxes(boxes[i], boxes[j])
                boxes[j] = np.array([-1,-1,-1,-1])
        boxes = boxes[~np.all(boxes == -1, axis=1)]
        boxes = np.unique(boxes, axis=0)
        return boxes

    def remove_small_boxes(self, boxes, W, H, threshold_perc = 0.01):
        wthresh = W * threshold_perc
        hthresh = H * threshold_perc
        for i in range(len(boxes)):
            box = boxes[i]
            if box[2] - box[0] < wthresh or box[3] - box[1] < hthresh:
                boxes[i] = (0, 0, 0, 0)
        boxes = boxes[~np.all(boxes == 0, axis=1)]
        return boxes

    def detectSWTandTransform(self, image, dark_on_light, chainBBs=None):
        boxes, draw, chainBBs = cv2.text.detectTextSWT(image, dark_on_light, chainBBs=chainBBs)
        for i in range(len(boxes)):
            boxes[i][2] = boxes[i][0] + boxes[i][2]
            boxes[i][3] = boxes[i][1] + boxes[i][3]
        return boxes

    def stroke_widths_transform(self, image, chainBBs=None):
        (H, W) = image.shape[:2]
        boxes = self.detectSWTandTransform(image, True, chainBBs)
        boxes2 = self.detectSWTandTransform(image, False, chainBBs)

        if len(boxes) == 0:
            boxes = boxes2
        elif len(boxes2) != 0:
            boxes = np.concatenate((boxes, boxes2))

        boxes = self.get_real_lines(boxes, W, H)
        boxes = self.remove_small_boxes(boxes, W, H, 0.015)
        for i in range(len(boxes)):
            boxes[i] = self.make_block_bigger(boxes[i], W, H, 15)

        return boxes
        
    def get_boxes_2(self, image):
        (H, W) = image.shape[:2]
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        # data = pytesseract.image_to_data(resized, config='--psm 11 --oem 1 -c tessedit_do_invert=0 -c tessedit_char_whitelist={}'.format('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'), output_type=pytesseract.Output.DICT)
        data = pytesseract.image_to_data(image, config='--psm 6 --oem 1 -c tessedit_do_invert=0', output_type=pytesseract.Output.DICT)
        count = len(data['level'])
        boxes = np.zeros((count, 4), dtype=np.int32)
        confs = np.zeros((count))
        num = 0
        for i in range(count):
            conf = float(data['conf'][i])
            x1 = int(data['left'][i])
            y1 = int(data['top'][i])
            x2 = (int(data['width'][i]) + x1)
            y2 = (int(data['height'][i]) + y1)
            word = data['text'][i]
            if conf < 95.:
                continue
            boxes[i] = self.make_block_bigger(np.array([x1, y1, x2, y2]), W, H, 1)
            confs[i] = conf
            num += 1
        boxes = boxes[~np.all(boxes == 0, axis=1)]
        confs = confs[confs != 0]
        boxes = self.get_real_lines(boxes, W, H)
        boxes = self.remove_small_boxes(boxes, W, H, 0.015)
        return {'image': image, 'boxes': boxes}

    def pattern_analysis(self, image):
        for pattern in self._patterns:
            pattern.reset()

        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        data_csv = pytesseract.image_to_data(image, config='--psm 12 --oem 1 -c tessedit_do_invert=0', output_type='string')
        log.error(data_csv)
        data_csv_lines = data_csv.splitlines()
        csv_reader = csv.reader(data_csv_lines, delimiter='\t')
        csv_reader.__next__() # skip head row
        for row in csv_reader:
            confidence = float(row[10])
            if confidence > 90:
                left = int(row[6])
                top = int(row[7])
                width = int(row[8])
                height = int(row[9])
                word_bounds = (left, top, left + width, top + height)

                for pattern in self._patterns:
                    pattern.bounds_contains(word_bounds)

        out_text = ''
        for pattern in self._patterns:
            if pattern.get_valid():
                out_text += 'Pattern is "' + pattern.name + '"\n'
        return out_text