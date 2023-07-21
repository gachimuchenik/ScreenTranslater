import pytesseract
import csv

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

    def pattern_analysis(self, image):
        for pattern in self._patterns:
            pattern.reset()

        pytesseract.pytesseract.tesseract_cmd = self._config.tesseract_path
        data_csv = pytesseract.image_to_data(image, config='--psm 11', output_type='string')
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