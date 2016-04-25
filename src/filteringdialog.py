import cv2
import numpy as np
from scipy import signal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QGraphicsScene, QSlider

from gui.filtering import Ui_Dialog
from src.datamanager import DataManager
from src.utils import toQImage


class FilteringDialog(QDialog, Ui_Dialog):
    scene = None
    image = None

    sliders = None

    def __init__(self, data_manager):
        super(FilteringDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        assert isinstance(data_manager, DataManager)
        self.image = data_manager.radiographs[0].image
        h, w = self.image.shape
        ch, cw = h/2, w/2
        self.image = self.image[ch - 100:ch + 500, cw-150:cw+150].copy()

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        ranges = [(0, 20), (0, 20), (0, 20), (0, 200), (0, 200)]
        values = [2, 8, 9, 0, 5]
        self.sliders = list()
        for i in range(0, len(ranges)):
            slider = QSlider(Qt.Horizontal, self.scrollAreaWidgetContents)
            slider.setRange(ranges[i][0], ranges[i][1])
            slider.setValue(values[i])
            slider.valueChanged.connect(self.slider_moved)
            self.scrollAreaWidgetContents.layout().addWidget(slider)
            self.sliders.append(slider)

        self._redraw()

    def slider_moved(self, value):
        self._redraw()

    def _sobel_filter(self, img):
        grad_x = cv2.Scharr(img, cv2.CV_64F, 1, 0) /16
        grad_y = cv2.Scharr(img, cv2.CV_64F, 0, 1) /16
        grad = np.sqrt(grad_x ** 2 + grad_y ** 2)
        return grad

    def _perform_fft(self, img):
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        return fshift

    def _redraw(self):
        img = self.image.copy()

        med_kernel = self.sliders[0].value() * 2 + 1
        bi_kernel = self.sliders[1].value() * 2 + 1
        bi_color = self.sliders[2].value()

        med = cv2.medianBlur(img, med_kernel)
        med_bi = cv2.bilateralFilter(med, bi_kernel, bi_color, 200)

        fshift = self._perform_fft(med_bi)
        # scharr = np.array([[ -1/16-1/16j, 1/2-1/8j,  +1/16 -1/16j],
        #                    [-1/8+0j, 1/2+0j, +1/8 +0j],
        #                    [ -1/16+1/16j, 0+1/8j,  +1/16 +1/16j]]) # Gx + j*Gy
        # fshift = signal.convolve2d(fshift, scharr, boundary='symm', mode='same')

        if self.sliders[3].value() != 0:
            rows, cols = img.shape
            crow, ccol = rows/2, cols/2
            mask = np.zeros(fshift.shape)
            cv2.circle(mask, (ccol, crow), self.sliders[3].value(), 1, -1)
            cv2.circle(mask, (ccol, crow), self.sliders[4].value(), 0, -1)
            fshift *= mask

        f_ishift = np.fft.ifftshift(fshift)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)

        grad_med_bi = self._sobel_filter(img_back)

        #img = (img / img.max()) * 255
        mag = 20*np.log(np.abs(fshift))
        mag = (mag / mag.max()) * 255
        img_back = (img_back / img_back.max()) * 255
        grad_med_bi = (grad_med_bi / grad_med_bi.max()) * 255

        together = np.hstack((img.astype(np.uint8), mag.astype(np.uint8), img_back.astype(np.uint8), grad_med_bi.astype(np.uint8)))
        cv2.imwrite("together.png", together)
        self.scene.addPixmap(QPixmap.fromImage(toQImage(together)))

        # self._focus_view()
