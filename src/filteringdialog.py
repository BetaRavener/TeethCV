import cv2
import numpy as np
from scipy import signal
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QGraphicsScene, QSlider, QBoxLayout, QHBoxLayout, QLabel

from gui.filtering import Ui_Dialog
from src.MultiresFramework import MultiResolutionFramework
from src.datamanager import DataManager
from src.utils import toQImage

__author__ = "Ivan Sevcik"

class FilteringDialog(QDialog, Ui_Dialog):
    scene = None
    base_image = None
    image = None
    current_sampling_level = 0

    sliders = None
    labels = None
    fit_allowed = False

    def __init__(self, data_manager):
        super(FilteringDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        assert isinstance(data_manager, DataManager)
        self.base_image = data_manager.radiographs[0].image
        h, w = self.base_image.shape
        ch, cw = h / 2, w / 2
        self.base_image = self.base_image[ch - 100:ch + 500, cw - 150:cw + 150].copy()
        self.image = self.base_image

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.levelSlider.setRange(1, MultiResolutionFramework.levels_count)
        self.levelSlider.setValue(self.current_sampling_level + 1)
        self.levelSlider.valueChanged.connect(self._sampling_level_changed)

        ranges = [(0, 20), (0, 20), (0, 20), (0, 200), (0, 200)]
        values = [2, 8, 9, 0, 5]
        self.sliders = list()
        self.labels = list()
        for i in range(0, len(ranges)):
            slider = QSlider(Qt.Horizontal, self.scrollAreaWidgetContents)
            label = QLabel()
            slider.setRange(ranges[i][0], ranges[i][1])
            slider.setValue(values[i])
            slider.valueChanged.connect(self._slider_moved)
            layout = QHBoxLayout()
            layout.addWidget(slider)
            layout.addWidget(label)
            self.scrollAreaWidgetContents.layout().addLayout(layout)
            self.sliders.append(slider)
            self.labels.append(label)

        self._set_labels()
        self._redraw()

    def _sampling_level_changed(self, value):
        self.current_sampling_level = value - 1

        self.image = self.base_image
        scale = 1.0
        for i in range(0, self.current_sampling_level):
            self.image = MultiResolutionFramework.downsample_image(self.image)
            scale *= 2

        self.graphicsView.resetTransform()
        self.graphicsView.scale(scale, scale)
        self._redraw()

    def _slider_moved(self, value):
        self._set_labels()
        self._redraw()

    def _set_labels(self):
        for i, label in enumerate(self.labels):
            value = self.sliders[i].value()
            if i < 2:
                value = value * 2 + 1 if value >= 1 else 0
            label.setText(str(value))

    def _scharr_filter(self, img):
        grad_x = cv2.Scharr(img, cv2.CV_64F, 1, 0) / 16
        grad_y = cv2.Scharr(img, cv2.CV_64F, 0, 1) / 16
        grad = np.sqrt(grad_x ** 2 + grad_y ** 2)
        return grad

    def _perform_fft(self, img):
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        return fshift

    def _focus_view(self, size):
        if not self.fit_allowed:
            self.fit_allowed = True
            return
        rect = QRectF(0, 0, size[0], size[1])
        self.scene.setSceneRect(rect)

    def _redraw(self):
        self.scene.clear()
        img = self.image.copy()

        med_kernel = self.sliders[0].value() * 2 + 1
        bi_kernel = self.sliders[1].value() * 2 + 1
        bi_color = self.sliders[2].value()

        med = cv2.medianBlur(img, med_kernel) if med_kernel > 1 else img
        med_bi = cv2.bilateralFilter(med, bi_kernel, bi_color, 200) if bi_kernel > 1 else med

        fshift = self._perform_fft(med_bi)
        # scharr = np.array([[ -1/16-1/16j, 1/2-1/8j,  +1/16 -1/16j],
        #                    [-1/8+0j, 1/2+0j, +1/8 +0j],
        #                    [ -1/16+1/16j, 0+1/8j,  +1/16 +1/16j]]) # Gx + j*Gy
        # fshift = signal.convolve2d(fshift, scharr, boundary='symm', mode='same')

        if self.sliders[3].value() != 0:
            rows, cols = img.shape
            crow, ccol = rows / 2, cols / 2
            mask = np.zeros(fshift.shape)
            cv2.circle(mask, (ccol, crow), self.sliders[3].value(), 1, -1)
            cv2.circle(mask, (ccol, crow), self.sliders[4].value(), 0, -1)
            fshift *= mask

        f_ishift = np.fft.ifftshift(fshift)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)

        grad_med_bi = self._scharr_filter(img_back)

        # img = (img / img.max()) * 255
        mag = 20 * np.log(np.abs(fshift))
        mag = (mag / mag.max()) * 255
        img_back = (img_back / img_back.max()) * 255
        grad_med_bi = (grad_med_bi / grad_med_bi.max()) * 255

        together = np.hstack(
            (img.astype(np.uint8), mag.astype(np.uint8), img_back.astype(np.uint8), grad_med_bi.astype(np.uint8)))
        cv2.imwrite("together.png", together)
        qimg = toQImage(together)
        self.scene.addPixmap(QPixmap.fromImage(qimg))

        self._focus_view((qimg.width(), qimg.height()))
