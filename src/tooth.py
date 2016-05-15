import os

import cv2
import numpy as np
from PyQt5.QtGui import QColor, QBrush, QFont, QPen
from PyQt5.QtWidgets import QGraphicsSimpleTextItem
import math

from src.utils import line_normal, create_rotation_matrix

__author__ = "Ivan Sevcik"

class Tooth(object):
    landmarks = None
    _centroid = None
    _normals = None

    landmark_size = 2
    outline_pen = QPen(QColor.fromRgb(255, 0, 0))
    point_pen = QPen(QColor.fromRgb(0, 255, 0))
    text_brush = QBrush(QColor.fromRgb(0, 0, 255))
    centroid_color = QColor.fromRgb(255, 255, 0)
    normals_pen = QPen(QColor.fromRgb(0, 255, 255))

    def __init__(self, landmarks):
        self.landmarks = landmarks
        self._calculate_centroid()

    def _calculate_centroid(self):
        self._centroid = np.mean(self.landmarks, axis=0)

    def _calculate_normals(self):
        point_count = self.landmarks.shape[0]
        left_normals = np.empty(self.landmarks.shape)
        right_normals = np.empty(self.landmarks.shape)
        for i, point in enumerate(self.landmarks):
            left_normals[i] = line_normal(self.landmarks[i - 1], point)
            right_normals[i] = line_normal(point, self.landmarks[(i + 1) % point_count])

        # Normalize normal vectors to have the same weight
        left_normals /= np.linalg.norm(left_normals, axis=1).reshape(40, 1)
        right_normals /= np.linalg.norm(right_normals, axis=1).reshape(40, 1)
        # Compute final normals and again normalize result
        self._normals = (left_normals + right_normals)
        self._normals /= np.linalg.norm(self._normals, axis=1).reshape(40, 1)

    def sum_of_squared_distances(self, other):
        """
        Calculates sum of squared distances between this and other shape
        :param other: Other object
        :return: Sum of squared distances
        """
        assert isinstance(other, Tooth)

        return np.sum((self.landmarks - other.landmarks) ** 2)

    def measure_error(self, other):
        '''
        Measures error between this and other shape. It can be used for comparing with correct shape during Leave one
        out analysis etc. In that case this should be the correct one.
        :param other: Shape for which the error against this one should be found.
        :return: Average error and maximum error
        '''

        # Center landmarks
        correct_landmarks = self.landmarks - self.centroid
        found_landmarks = other.landmarks - other.centroid

        differences = np.linalg.norm(found_landmarks - correct_landmarks, axis=1)
        distances = np.linalg.norm(correct_landmarks, axis=1)
        errors = differences / distances

        return np.average(errors), np.max(errors)
        #TODO: Delete
        #np.linalg.norm(predicted - actual_points, 2) / np.linalg.norm(actual_points, 2)

    def align(self, other):
        """
        Uses procrustes analysis to align this shape to the other.
        :param other: Object to which this one should align. Must be at origin and unit sized.
        :returns Translation vector, scale factor and angle by which can be aligned shape transformed to its original.
        """
        translation = self.centroid
        self.move_to_origin()
        scale = self.normalize_shape()

        x = self.landmarks[:, 0]
        y = self.landmarks[:, 1]
        w = other.landmarks[:, 0]
        z = other.landmarks[:, 1]
        top_sum = np.sum(w * y - z * x)
        bottom_sum = np.sum(w * x + z * y)
        angle = math.atan(top_sum / bottom_sum)

        self.rotate(angle)
        return translation, scale, -angle

    def move_to_origin(self):
        """
        Moves all landmarks so that centroid is at the origin (0,0)
        """
        self.translate(-self.centroid)

    def normalize_shape(self):
        """
        Normalizes shape X so that |X| = 1.
        Uses Root Mean Squares
        """
        # Calculate vectors from origin to each landmark
        scaling_factor = self.landmarks - self.centroid
        # Square distances
        scaling_factor **= 2
        # Sum all distances
        scaling_factor = np.sum(scaling_factor)
        # Divide by number of elements and get square root
        scaling_factor = np.sqrt(scaling_factor / self.landmarks.size)

        self.scale(1 / scaling_factor)
        return scaling_factor

    def rotate(self, angle):
        rot_matrix = create_rotation_matrix(angle)
        self.landmarks = self.landmarks.dot(rot_matrix)
        self._normals = None
        self._centroid = None

    def scale(self, factor):
        self.landmarks *= factor
        self._normals = None
        self._centroid = None

    def translate(self, vec):
        self.landmarks = self.landmarks + vec
        self._centroid = None

    def transform(self, translation_vector, scale_factor, rotation_angle):
        """
        Performs rotation, scaling and translation (in this order)
        """
        self.rotate(rotation_angle)
        self.scale(scale_factor)
        self.translate(translation_vector)

    def downsample_transform(self):
        '''
        Performs transform that should be applied to a tooth after downsampling image once
        '''
        self.scale(0.5)

    def upsample_transform(self):
        '''
        Performs transform that should be applied to a tooth after upsampling image once
        '''
        self.scale(2)

    def draw(self, scene, outline=True, landmarks=False, text=False, normals=False):
        count = self.landmarks.shape[0]

        if outline:
            for i in range(0, count):
                scene.addLine(self.landmarks[i][0], self.landmarks[i][1], self.landmarks[(i + 1) % count][0],
                              self.landmarks[(i + 1) % count][1], pen=self.outline_pen)

        if landmarks:
            for i in range(0, count):
                scene.addEllipse(self.landmarks[i][0] - self.landmark_size, self.landmarks[i][1] - self.landmark_size,
                                 self.landmark_size * 2, self.landmark_size * 2, pen=self.point_pen)

            scene.addEllipse(self.centroid[0] - self.landmark_size, self.centroid[1] - self.landmark_size,
                             self.landmark_size * 2, self.landmark_size * 2,
                             pen=QPen(self.centroid_color), brush=QBrush(self.centroid_color))

        if normals:
            length = self.normals_pen.widthF() * 15
            for i, normal in enumerate(self.normals):
                landmark = self.landmarks[i]
                assert isinstance(landmark, np.ndarray)

                pt1 = landmark - normal * length
                pt2 = landmark + normal * length
                scene.addLine(pt1[0], pt1[1], pt2[0], pt2[1], pen=self.normals_pen)

        if text:
            for i in range(0, count):
                font = QFont("Times", 6)
                text = scene.addSimpleText(str(i), font=font)
                assert isinstance(text, QGraphicsSimpleTextItem)
                text.setPos(self.landmarks[i][0] + self.landmark_size,
                            self.landmarks[i][1] - text.boundingRect().height() / 2)
                text.setBrush(self.text_brush)

    def export_landmarks(self, name_suffix, directory="./data/Out"):
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = directory + ("/landmarks-%s.txt" % name_suffix)
        np.savetxt(filename, self.landmarks.flatten(), "%.6f")

    def export_segmentation(self, name_suffix, image_dimensions, directory="./data/Out"):
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = directory + ("/segment-%s.png" % name_suffix)
        img = np.zeros(image_dimensions)
        cv2.fillConvexPoly(img, self.landmarks.astype(np.int32), 255)
        cv2.imwrite(filename, img)

    @property
    def normals(self):
        if self._normals is None:
            self._calculate_normals()

        return self._normals

    @property
    def centroid(self):
        if self._centroid is None:
            self._calculate_centroid()

        return self._centroid