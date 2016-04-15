from copy import deepcopy

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QBrush
from PyQt5.QtWidgets import QDialog, QGraphicsScene
from sklearn import decomposition

from gui.trainer import Ui_Trainer
from src.datamanager import DataManager
from src.tooth import Tooth


class TrainerDialog(QDialog, Ui_Trainer):
    scene = None
    data_manager = None
    tooth1 = None
    tooth2 = None
    align_step = 0

    eigvals = None
    eigvecs = None

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
        self.choiceSlider.setRange(1, len(teeth))
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
        teeth = self.data_manager.get_all_teeth(True)
        mean_shape = deepcopy(teeth[0])
        assert isinstance(mean_shape, Tooth)
        mean_shape.move_to_origin()
        mean_shape.normalize_shape()

        error = float("inf")
        while error > 0.05:
            meanAcum = np.zeros(mean_shape.landmarks.shape)
            for i in range(0, len(teeth)):
                teeth[i].align(mean_shape)
                meanAcum += teeth[i].landmarks

            new_mean_shape = Tooth(meanAcum / len(teeth))
            new_mean_shape.align(mean_shape)
            error = new_mean_shape.sum_of_squared_distances(mean_shape)

            print error

            mean_shape = new_mean_shape

        self.scene.clear()
        mean_shape.outline_pen = QPen(QColor.fromRgb(255, 0, 0))
        mean_shape.outline_pen.setWidthF(0.02)
        mean_shape.draw(self.scene, True, False, False)
        self._focus_view()

        # TODO: What layout should be used? 1: x,y,x,y... or 2: x,x,x...,y,y,y...
        data = np.zeros((112, 80))
        for i, tooth in enumerate(teeth):
            data[i, :] = tooth.landmarks.flatten()

        self.eigvals, self.eigvecs = self.pca(deepcopy(data), mean_shape.landmarks.flatten())

    @staticmethod
    def pca(data, mean, pc_count=None):
        """
        Does principal component analysis on data
        :param data: Input data (rows are features, columns are samples)
        :param mean: Mean of input data
        :param pc_count: Number of components to return (None returns all)
        :return: Array of eigenvalues and matrix of eigenvectors (each row is eigenvector)
        """
        demeaned = data - mean
        pca = decomposition.PCA(n_components=pc_count, whiten=False).fit(demeaned)

        eigvals = pca.explained_variance_ratio_ / np.linalg.norm(pca.explained_variance_ratio_)
        eigvecs = pca.components_

        if pc_count is None:
            pc_count = len(eigvals)

        order = eigvals.argsort()[::-1]

        return eigvals[order[0:pc_count]], eigvecs[:, order[0:pc_count]].T
