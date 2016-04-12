import sys

import cv2
import numpy as np
from PyQt5.QtGui import QImage, qRgb, QPixmap, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene

from gui.mainwindow import Ui_MainWindow

gray_color_table = [qRgb(i, i, i) for i in range(256)]


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


class MainWindow(QMainWindow, Ui_MainWindow):
    current_sample = 0
    current_scale = 0

    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.setupUi(self)

        self.load_sample(self.current_sample)

        # Connect up the buttons.
        # self.okButton.clicked.connect(self.accept)
        # self.cancelButton.clicked.connect(self.reject)
        self.horizontalSlider.setValue(self.current_sample)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(14)
        self.horizontalSlider.valueChanged.connect(self.set_sample)

        self.horizontalSlider_2.setMinimum(-10)
        self.horizontalSlider_2.setMaximum(10)
        self.horizontalSlider_2.setValue(self.current_scale)
        self.horizontalSlider_2.valueChanged.connect(self.change_scale)

    def set_sample(self, sampleId):
        self.current_sample = sampleId - 1
        self.load_sample(self.current_sample)

    def change_scale(self, scale):
        self.current_scale = scale
        self.graphicsView.resetTransform()
        real_scale = 1 + scale * (0.1 if scale >= 0 else 0.05)
        self.graphicsView.scale(real_scale, real_scale)

    def draw_landmarks(self, scene, landmarks):
        assert isinstance(scene, QGraphicsScene)
        assert isinstance(landmarks, np.ndarray)

        outline_pen = QPen(QColor.fromRgb(255, 0, 0))
        point_pen = QPen(QColor.fromRgb(0, 255, 0))
        point_size = 2

        count = landmarks.shape[0]
        for i in range(0, count):
            scene.addLine(landmarks[i][0], landmarks[i][1], landmarks[(i + 1) % count][0],
                          landmarks[(i + 1) % count][1], pen=outline_pen)
        for i in range(0, count):
            scene.addEllipse(landmarks[i][0] - point_size, landmarks[i][1] - point_size,
                             point_size * 2, point_size * 2, pen=point_pen)

    def read_landmarks(self, filename):
        with open(filename) as landmarks_file:
            arr = np.array(landmarks_file.readlines(), dtype=float)

        if arr is not None:
            arr = arr.reshape((arr.shape[0] / 2, 2))

        return arr

    def load_sample(self, idx):
        scene = QGraphicsScene()

        # Load and draw image
        cv_img = cv2.imread('./data/Radiographs/%02d.tif' % (idx + 1))
        img = toQImage(cv_img)
        scene.addPixmap(QPixmap.fromImage(img))

        # Load and draw landmarks
        for i in range(0, 8):
            landmarks = self.read_landmarks('./data/Landmarks/original/landmarks%d-%d.txt' % (idx + 1, i + 1))
            self.draw_landmarks(scene, landmarks)

        # Set generated scene into the view
        self.graphicsView.setScene(scene)
        self.graphicsView.resetTransform


# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)

    ex2 = MainWindow()
    ex2.show()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
