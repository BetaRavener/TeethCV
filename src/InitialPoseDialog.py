import numpy as np
import cv2

from scipy.signal import argrelextrema
from PyQt5.QtCore import Qt, QRectF, QLine, QLineF
from PyQt5.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt5.QtWidgets import QDialog, QGraphicsScene, QFileDialog

from gui.initpose import Ui_PoseDialog
from src.InitialPoseModel import InitialPoseModel
from src.datamanager import DataManager
from src.radiograph import Radiograph
from src.utils import toQImage
from src.filter import Filter


class InitialPoseDialog(QDialog, Ui_PoseDialog):
    data_manager = None
    image = None
    y_line = 0
    y_top_line = 0
    y_lower_line = 0
    landmark_size = 2
    lines = None
    middle_idx = 0
    pose_model = None

    def __init__(self, data_manager):
        super(InitialPoseDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager
        self.pose_model = InitialPoseModel(data_manager)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.image = Filter.crop_image(self.data_manager.radiographs[0].image)

        self.findButton.clicked.connect(self.find_jaw_divider)
        self.openButton.clicked.connect(self._open_radiograph)

        self._redraw()

    def find_jaw_divider(self):
        self.y_top_line, self.y_lower_line = self.pose_model._find_jaw_separation_line(self.pose_model._crop_image_sides(self.image))

        upper_jaw_image = self.pose_model.crop_top_jaw(self.image, self.y_top_line)
        lower_jaw_image = self.pose_model.crop_lower_jaw(self.image, self.y_lower_line)

        # Filter the image
        upper_jaw_image = Filter.process_image(upper_jaw_image, median_kernel=5, bilateral_kernel=17, bilateral_color=6)
        lower_jaw_image = Filter.process_image(lower_jaw_image, median_kernel=5, bilateral_kernel=17, bilateral_color=6)

        upper_jaw_image = self.pose_model._convert_to_binary_image(upper_jaw_image)
        lower_jaw_image = self.pose_model._convert_to_binary_image(lower_jaw_image)

        upper_lines = self.pose_model._find_hough_lines(upper_jaw_image, threshold=15)
        lower_lines = self.pose_model._find_hough_lines(lower_jaw_image, threshold=15)

        # Filter out lines
        upper_lines = self.pose_model._filter_lines(upper_lines, upper_jaw_image.shape, line_offset=6, max_line_gap=90)
        lower_lines = self.pose_model._filter_lines(lower_lines, lower_jaw_image.shape, line_offset=2, max_line_gap=60)

        self.image = lower_jaw_image
        self.lines = lower_lines
        self._redraw()

    def _open_radiograph(self):
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory("./data/Radiographs")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Radiograph (*.tif)")
        if file_dialog.exec_() and len(file_dialog.selectedFiles()) == 1:
            radiograph = Radiograph()
            radiograph.path_to_img = file_dialog.selectedFiles()[0]
            #self.image = radiograph.image
            #crop_translation = -Filter.get_cropping_region(radiograph.image).left_top
            self.image = Filter.crop_image(radiograph.image)
            self.lines = None
            self._redraw()

    def _redraw(self, normalize=False):
        self.scene.clear()

        img = self.image.copy()

        if normalize:
            img = (img / img.max()) * 255

        # Draw image
        qimg = toQImage(img.astype(np.uint8))
        self.scene.addPixmap(QPixmap.fromImage(qimg))

        # Add jaws divider
        self.scene.addLine(QLineF(0, self.y_line, self.image.shape[1], self.y_line), pen=QPen(QColor.fromRgb(255, 0, 0)))
        self.scene.addLine(QLineF(0, self.y_top_line, self.image.shape[1], self.y_top_line), pen=QPen(QColor.fromRgb(255, 0, 0)))
        self.scene.addLine(QLineF(0, self.y_lower_line, self.image.shape[1], self.y_lower_line), pen=QPen(QColor.fromRgb(255, 0, 0)))


        # Add image center
        self.scene.addEllipse(self.image.shape[0]/2 - self.landmark_size, self.image.shape[1]/2 - self.landmark_size,
                             self.landmark_size * 2, self.landmark_size * 2,
                             pen=QPen(QColor.fromRgb(255, 0, 0)), brush=QBrush(QColor.fromRgb(255, 0, 0)))

        # Draw Hough lines
        if self.lines is not None:
            #for x1,y1,x2,y2 in self.lines[0]:
            for i, line_param in enumerate(self.lines):
                    rho,theta = line_param
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 200*(-b))
                    y1 = int(y0 + 200*(a))
                    x2 = int(x0 - 200*(-b))
                    y2 = int(y0 - 200*(a))
                    self.scene.addLine(QLineF(x1, y1, x2, y2), pen=QPen(QColor.fromRgb(0, 255, 0)))


