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
        self.net = cv2.dnn.readNet(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'frozen_east_text_detection.pb'))
        
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
    
    def get_boxes(self, image):
        layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"]
        (H, W) = image.shape[:2]

        newW = 320
        newH = 320
        rW = W / float(newW)
        rH = H / float(newH)
        resized = cv2.resize(image, (newW, newH))
        (H, W) = resized.shape[:2]

        blob = cv2.dnn.blobFromImage(resized, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
        start = time.time()
        self.net.setInput(blob)
        (scores, geometry) = self.net.forward(layerNames)
        end = time.time()

        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []
        # loop over the number of rows
        for y in range(0, numRows):
            # extract the scores (probabilities), followed by the geometrical
            # data used to derive potential bounding box coordinates that
            # surround text
            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]
            	# loop over the number of columns
            for x in range(0, numCols):
                # if our score does not have sufficient probability, ignore it
                if scoresData[x] < 0.5:
                    continue
                # compute the offset factor as our resulting feature maps will
                # be 4x smaller than the input image
                (offsetX, offsetY) = (x * 4.0, y * 4.0)
                # extract the rotation angle for the prediction and then
                # compute the sin and cosine
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)
                # use the geometry volume to derive the width and height of
                # the bounding box
                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]
                # compute both the starting and ending (x, y)-coordinates for
                # the text prediction bounding box
                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)
                # add the bounding box coordinates and probability score to
                # our respective lists
                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])
            # apply non-maxima suppression to suppress weak, overlapping bounding
            # boxes
        boxes = non_max_suppression(np.array(rects), probs=confidences)
        # loop over the bounding boxes
        boxes = self.make_bigger_blocks(boxes, W, H)
        boxes = self.get_lines(boxes)
        for box in boxes:
            # scale the bounding box coordinates based on the respective
            # ratios
            box[0] = int(box[0] * rW)
            box[1] = int(box[1] * rH)
            box[2] = int(box[2] * rW)
            box[3] = int(box[3] * rH)
            # cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        log.info(f'boxes={boxes}')
        return {'image': image, 'boxes': boxes}
    
    def make_bigger_blocks(self, boxes, W, H):
        for box in boxes:
            w = int(((box[2] - box[0]) / 100.0) * 50)
            h = int(((box[3] - box[1]) / 100.0) * 50)
            box[0] = max(box[0] - w, 0)
            box[1] = max(box[1] - h, 0)
            box[2] = min(box[2] + w, W)
            box[3] = min(box[3] + h, H)
        return boxes

    def get_lines(self, boxes):
        for i in range(len(boxes)):
            if boxes[i][0] == -1 and boxes[i][1] == -1 and boxes[i][2] == -1 and boxes[i][3] == -1:
                continue
            for j in range(i+1, len(boxes)):
                if boxes[j][0] == -1 and boxes[j][1] == -1 and boxes[j][2] == -1 and boxes[j][3] == -1:
                    continue
                if boxes[i][3] < boxes[j][1] or boxes[i][1] > boxes[j][3]:
                    continue
                boxes[i][0] = min(boxes[i][0], boxes[j][0])
                boxes[i][1] = min(boxes[i][1], boxes[j][1])
                boxes[i][2] = max(boxes[i][2], boxes[j][2])
                boxes[i][3] = max(boxes[i][3], boxes[j][3])
                boxes[j] = np.array([-1,-1,-1,-1])
        boxes = boxes[~np.all(boxes == -1, axis=1)]
        return boxes
    
    def get_boxes_2(self, image):
        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        data_csv = pytesseract.image_to_data(image, config='--psm 12 --oem 1 -c tessedit_do_invert=0', output_type='string')
        log.error(data_csv)
        data_csv_lines = data_csv.splitlines()
        csv_reader = csv.reader(data_csv_lines, delimiter='\t')
        csv_reader.__next__() # skip head row
        boxes = np.zeros((len()))
        for row in csv_reader:
            confidence = float(row[10])
            if confidence > 90:
                left = int(row[6])
                top = int(row[7])
                width = int(row[8])
                height = int(row[9])
                word_bounds = (left, top, left + width, top + height)
                boxes.append()

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