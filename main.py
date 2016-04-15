import sys

import numpy as np
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QImage, qRgb, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QDialog

from gui.mainwindow import Ui_MainWindow
from gui.trainer import Ui_Trainer
from src.datamanager import DataManager
from src.trainerdialog import TrainerDialog

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


class InteractiveGraphicsScene(QGraphicsScene):
    clicked = pyqtSignal()

    def __init__(self):
        super(QGraphicsScene, self).__init__()

    def mouseReleaseEvent(self, QGraphicsSceneMouseEvent):
        self.clicked.emit()


class MainWindow(QMainWindow, Ui_MainWindow):
    scene = None
    data_manager = None

    current_sample = 0
    current_scale = 0

    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.setupUi(self)

        self.scene = InteractiveGraphicsScene()
        # self.scene.clicked.connect()

        self.data_manager = DataManager()

        self.graphicsView.setScene(self.scene)

        self.display_radiograph(self.current_sample)

        # Connect up the buttons.
        # self.okButton.clicked.connect(self.accept)
        # self.cancelButton.clicked.connect(self.reject)
        self.radiographSlider.setValue(self.current_sample)
        self.radiographSlider.setMinimum(1)
        self.radiographSlider.setMaximum(self.data_manager.number_of_radiographs)
        self.radiographSlider.valueChanged.connect(self.set_sample)

        self.zoomSlider.setMinimum(-10)
        self.zoomSlider.setMaximum(10)
        self.zoomSlider.setValue(self.current_scale)
        self.zoomSlider.valueChanged.connect(self.change_scale)

        self.trainerButton.clicked.connect(self.open_trainer)

    def open_trainer(self):
        dialog = TrainerDialog(self.data_manager)
        dialog.exec_()

    def set_sample(self, sampleId):
        self.current_sample = sampleId - 1
        self.display_radiograph(self.current_sample)

    def change_scale(self, scale):
        self.current_scale = scale
        self.graphicsView.resetTransform()
        real_scale = 1 + scale * (0.1 if scale >= 0 else 0.05)
        self.graphicsView.scale(real_scale, real_scale)

    def display_radiograph(self, idx):
        self.scene.clear()

        radiograph = self.data_manager.radiographs[idx]

        # Load and draw image
        img = toQImage(radiograph.image)
        self.scene.addPixmap(QPixmap.fromImage(img))

        for tooth in radiograph.teeth:
            tooth.draw(self.scene, True, True, True)

        # Set generated scene into the view
        self.graphicsView.resetTransform()
        self.graphicsView.centerOn(self.scene.width() / 2, self.scene.height() / 2)
        self.current_scale = 0
        self.zoomSlider.setValue(0)


# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)

    ex2 = MainWindow()
    ex2.show()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
