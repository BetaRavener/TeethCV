import math
from copy import deepcopy

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QDialog, QGraphicsScene, QSlider

from gui.pcavisualizer import Ui_PcaVisualizerDialog
from src.datamanager import DataManager
from src.pca import PCA
from src.tooth import Tooth
from src.utils import to_landmarks_format


class PcaVisualizerDialog(QDialog, Ui_PcaVisualizerDialog):
    slider_resolution = 1000
    ignore_sliders = False
    scene = None
    pca = None
    _scales = None
    combined = None
    data_manager = None

    def __init__(self, pca, data_manager):
        super(PcaVisualizerDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        assert isinstance(pca, PCA)
        assert isinstance(data_manager, DataManager)
        self.pca = pca
        self.data_manager = data_manager

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor.fromRgb(50, 50, 50)))
        self.graphicsView.setScene(self.scene)

        self._scales = np.empty(self.pca.eigen_values.shape)
        for i, deviation in enumerate(self.pca.get_allowed_deviation()):
            slider = QSlider(Qt.Horizontal, self.scrollAreaWidgetContents)
            slider.setRange(-self.slider_resolution, self.slider_resolution)
            slider.valueChanged.connect(self.slider_moved)
            self.scrollAreaWidgetContents.layout().addWidget(slider)
            self._scales[i] = deviation / self.slider_resolution

        self.resetButton.clicked.connect(self.reset)

        self.choiceSlider.setRange(0, self.data_manager.count_all_teeth()-1)
        self.choiceSlider.valueChanged.connect(self.set_from_projection)

        self.reset()

    def _get_all_sliders(self):
        sliders = list()
        for i in range(0, self.scrollAreaWidgetContents.layout().count()):
            item = self.scrollAreaWidgetContents.layout().itemAt(i).widget()
            if isinstance(item, QSlider):
                sliders.append(item)

        return sliders

    def reset(self):
        self.ignore_sliders = True
        for i, slider in enumerate(self._get_all_sliders()):
            slider.setValue(0)
        self.ignore_sliders = False

        self.combined = np.copy(self.pca.mean)
        self._redraw()

    def slider_moved(self, value):
        if self.ignore_sliders:
            return

        self.combined = self._compute_shape()
        self._redraw()

    def set_from_projection(self, idx):
        tooth = self.data_manager.get_tooth_from_all(idx, True)
        mean_tooth = Tooth(to_landmarks_format(self.pca.mean))
        tooth.align(mean_tooth)
        data = tooth.landmarks.flatten()
        params = self.pca.project(data)

        slider_values = params / self._scales
        self.ignore_sliders = True
        for i, slider in enumerate(self._get_all_sliders()):
            slider.setValue(int(slider_values[i]))
        self.ignore_sliders = False

        self.combined = self._compute_shape(params)
        self._redraw(tooth)

    def _compute_shape(self, params=None):
        if params is None:
            params = np.empty(self.pca.eigen_values.shape)
            sliders = self._get_all_sliders()
            for i, scale in enumerate(self._scales):
                params[i] = sliders[i].value() * scale

        return self.pca.reconstruct(params)

    def _redraw(self, original_tooth=None):
        tooth = Tooth(to_landmarks_format(self.combined))

        self.scene.clear()

        if original_tooth is not None:
            original_tooth = deepcopy(original_tooth)
            original_tooth.outline_pen = QPen(QColor.fromRgb(0, 255, 255))
            original_tooth.outline_pen.setWidthF(0.02)
            original_tooth.draw(self.scene, True, False, False)

        tooth.outline_pen.setWidthF(0.02)
        tooth.draw(self.scene, True, False, False)

        self._focus_view()

    def _focus_view(self):
        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)
        self.graphicsView.fitInView(rect, Qt.KeepAspectRatio)
