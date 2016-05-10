from copy import deepcopy

import numpy as np
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QDialog, QGraphicsScene

from gui.trainer import Ui_Trainer
from src.StatisticalShapeModel import StatisticalShapeModel
from src.datamanager import DataManager
from src.pca import PCA
from src.tooth import Tooth
from src.utils import to_landmarks_format

__author__ = "Ivan Sevcik"


class TrainerDialog(QDialog, Ui_Trainer):
    scene = None
    data_manager = None
    tooth1 = None
    tooth2 = None
    align_step = 0

    pca = None

    trained = pyqtSignal(PCA)

    def __init__(self, data_manager):
        super(TrainerDialog, self).__init__()
        self.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor.fromRgb(50, 50, 50)))
        self.graphicsView.setScene(self.scene)

        self.alignButton.clicked.connect(self.make_step)
        self.trainButton.clicked.connect(self.train)

        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager

        self.change_teeth(1)
        teeth = data_manager.get_all_teeth(False)
        self.choiceSlider.setRange(1, len(teeth) - 1)
        self.choiceSlider.valueChanged.connect(self.change_teeth)

    def change_teeth(self, idx):
        teeth = self.data_manager.get_all_teeth(True)
        self.tooth1 = teeth[0]
        self.tooth2 = teeth[idx]

        self.tooth1.outline_pen = QPen(QColor.fromRgb(255, 0, 0))
        self.tooth2.outline_pen = QPen(QColor.fromRgb(0, 255, 0))

        self.scene.clear()
        self.tooth1.draw(self.scene, True, False, False)
        self.tooth2.draw(self.scene, True, False, False)
        self._focus_view()
        self.align_step = 0

    def make_step(self):
        if self.align_step == 3:
            return

        if self.align_step == 0:
            self.tooth1.move_to_origin()
            self.tooth2.move_to_origin()

        if self.align_step == 1:
            self.tooth1.normalize_shape()
            self.tooth2.normalize_shape()
            self.tooth1.outline_pen.setWidthF(0.02)
            self.tooth2.outline_pen.setWidthF(0.02)

        if self.align_step == 2:
            self.tooth2.align(self.tooth1)

        self.scene.clear()
        self.tooth1.draw(self.scene, True, False, False)
        self.tooth2.draw(self.scene, True, False, False)
        self._focus_view()
        self.align_step += 1

    def _focus_view(self):
        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)
        self.graphicsView.fitInView(rect, Qt.KeepAspectRatio)

    def train(self):
        self.pca = StatisticalShapeModel.create(self.data_manager)
        self.pca.threshold(self.thresholdSpinBox.value())
        self._show_training_result()

        self.trained.emit(self.pca)

    def _show_training_result(self):
        mean_tooth = Tooth(to_landmarks_format(self.pca.mean))
        test_tooth = self.data_manager.get_tooth(0, 0, True)
        test_tooth.align(mean_tooth)

        tooth_data = test_tooth.landmarks.flatten()
        projection = self.pca.project(tooth_data)
        reconstructed_data = self.pca.reconstruct(projection)

        shapes = [self.pca.mean, tooth_data, reconstructed_data]
        colors = [[255, 0, 0], [0, 255, 255], [255, 255, 0]]

        self.scene.clear()
        for i, shape in enumerate(shapes):
            tooth = Tooth(to_landmarks_format(shape))
            r, g, b = colors[i]
            tooth.outline_pen = QPen(QColor.fromRgb(r, g, b))
            tooth.outline_pen.setWidthF(0.02)
            tooth.draw(self.scene, True, False, False)

        self._focus_view()
        self.compCountLabel.setText(str(len(self.pca.eigen_values)))
