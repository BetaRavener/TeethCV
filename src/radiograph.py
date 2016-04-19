import cv2
import numpy as np

from src.tooth import Tooth


def read_landmarks(filename):
    with open(filename) as landmarks_file:
        arr = np.array(landmarks_file.readlines(), dtype=float)

    if arr is not None:
        arr = arr.reshape((arr.shape[0] / 2, 2))

    return arr


class Radiograph:
    teeth = None
    idx = None
    path_to_img = None

    def __init__(self):
        self.teeth = list()

    def load(self, idx, annotated=False):
        self.idx = idx

        # Load and draw landmarks
        if annotated:
            for i in range(0, 4):
                landmarks = read_landmarks('./data/Landmarks/original/landmarks%d-%d.txt' % (idx + 1, i + 1))
                self.teeth.append(Tooth(landmarks))

        self.path_to_img = './data/Radiographs/%02d.tif' % (self.idx + 1)

    @property
    def image(self):
        return cv2.cvtColor(cv2.imread(self.path_to_img), cv2.COLOR_BGR2GRAY)
