import sys
from copy import deepcopy

import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, Qt, QRect, QRectF
from PyQt5.QtGui import QImage, qRgb, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QDialog

from gui.mainwindow import Ui_MainWindow
from gui.trainer import Ui_Trainer
from src.InitialPoseDialog import InitialPoseDialog
from src.MultiresFramework import MultiResolutionFramework
from src.datamanager import DataManager
from src.filteringdialog import FilteringDialog
from src.fitterdialog import FitterDialog
from src.interactivegraphicsscene import InteractiveGraphicsScene
from src.pcavisualizerdialog import PcaVisualizerDialog
from src.sampler import Sampler
from src.trainerdialog import TrainerDialog
from src.utils import toQImage

__author__ = "Ivan Sevcik"


class MainWindow(QMainWindow, Ui_MainWindow):
    scene = None
    data_manager = None

    current_sample = 0
    current_scale = 0
    sampling_level = 0

    pca = None
    mean_shape = None

    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.setupUi(self)

        self.scene = InteractiveGraphicsScene()
        # self.scene.clicked.connect()

        self.data_manager = DataManager()
        self.data_manager.select_lower_jaw()
        #self.data_manager.select_upper_jaw()

        self.graphicsView.setScene(self.scene)

        self.display_radiograph(self.current_sample)

        self.radiographSlider.setValue(self.current_sample + 1)
        self.radiographSlider.setRange(1, self.data_manager.number_of_radiographs)
        self.radiographSlider.valueChanged.connect(self.set_sample)

        self.zoomSlider.setRange(-10, 10)
        self.zoomSlider.setValue(self.current_scale)
        self.zoomSlider.valueChanged.connect(self.change_scale)

        self.levelSlider.setRange(1, MultiResolutionFramework.levels_count)
        self.levelSlider.setValue(self.sampling_level + 1)
        self.levelSlider.valueChanged.connect(self.change_sampling_level)

        self.trainerButton.clicked.connect(self.open_trainer)
        self.filteringButton.clicked.connect(self.open_filtering)

        self.pcaVisualizerButton.setEnabled(False)
        self.pcaVisualizerButton.clicked.connect(self.open_pca_visulalizer)

        self.fitterButton.setEnabled(False)
        self.fitterButton.clicked.connect(self.open_fitter)

        self.initializationButton.clicked.connect(self.open_initialize_pose)

    def open_trainer(self):
        dialog = TrainerDialog(self.data_manager)
        dialog.trained.connect(self.save_training)
        dialog.exec_()

    def open_filtering(self):
        dialog = FilteringDialog(self.data_manager)
        dialog.exec_()

    def save_training(self, pca):
        self.pca = pca
        self.pcaVisualizerButton.setEnabled(True)
        self.fitterButton.setEnabled(True)

    def open_pca_visulalizer(self):
        dialog = PcaVisualizerDialog(self.pca, self.data_manager)
        dialog.exec_()

    def open_fitter(self):
        dialog = FitterDialog(self.data_manager, self.pca)
        dialog.exec_()

    def open_initialize_pose(self):
        dialog = InitialPoseDialog(self.data_manager)
        dialog.exec_()

    def set_sample(self, sampleId):
        self.current_sample = sampleId - 1
        self.display_radiograph(self.current_sample)

    def change_scale(self, scale):
        self.current_scale = scale
        self.graphicsView.resetTransform()
        real_scale = 1 + scale * (0.1 if scale >= 0 else 0.05)
        self.graphicsView.scale(real_scale, real_scale)

    def change_sampling_level(self, sampling_level):
        self.sampling_level = sampling_level - 1
        self.display_radiograph(self.current_sample)

    def display_radiograph(self, idx):
        self.scene.clear()

        radiograph = self.data_manager.radiographs[idx]

        image = radiograph.image
        teeth = self.data_manager.get_all_teeth_from_radiograph(radiograph, True)

        # Apply sampling level
        for i in range(0, self.sampling_level):
            image, teeth = MultiResolutionFramework.downsample(image, teeth)

        # Load and draw image
        qimg = toQImage(image)
        size = (qimg.width(), qimg.height())
        self.scene.addPixmap(QPixmap.fromImage(qimg))

        for tooth in teeth:
            tooth.draw(self.scene, True, True, True)

        # Set generated scene into the view
        self.scene.setSceneRect(QRectF(0, 0, size[0], size[1]))
        self.graphicsView.resetTransform()
        self.graphicsView.centerOn(self.scene.width() / 2, self.scene.height() / 2)
        self.current_scale = 0
        self.zoomSlider.setValue(0)
        self.update_size_label(size)

    def update_size_label(self, size):
        self.sizeLabel.setText("%d, %d" % size)


# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)

    ex2 = MainWindow()
    ex2.show()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
