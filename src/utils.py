import numpy as np
from PyQt5.QtGui import QImage, qRgb

__author__ = "Ivan Sevcik"

gray_color_table = [qRgb(gctIdx, gctIdx, gctIdx) for gctIdx in range(256)]


class NotImplementedException(object):
    pass


def toQImage(im, copy=False):
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888)
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32)
                return qim.copy() if copy else qim

    raise NotImplementedException


def line_normal(pt1, pt2):
    # Find line vector
    vec = (pt1 - pt2)
    # Swap coordinates and negate one of them to find normal
    return vec[1], -vec[0]


def to_landmarks_format(vec):
    return vec.reshape(vec.size / 2, 2)


def create_rotation_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle), np.cos(angle)]])


class Rectangle:
    top = None
    bottom = None
    left = None
    right = None

    def __init__(self, left, top, right, bottom):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    @property
    def left_top(self):
        return np.array((self.left, self.top))


class StopIterationToken(object):
    stop = False
