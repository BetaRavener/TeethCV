from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from gui.simplescenewindow import Ui_SimpleSceneWindow

__author__ = "Ivan Sevcik"


class SimpleSceneWindow(QMainWindow, Ui_SimpleSceneWindow):
    current_scale = 0

    def __init__(self):
        super(SimpleSceneWindow, self).__init__()
        self.setupUi(self)

        #self.setAttribute(Qt.WA_DeleteOnClose)

        self.zoomSlider.setRange(-10, 10)
        self.zoomSlider.setValue(self.current_scale)
        self.zoomSlider.valueChanged.connect(self._change_scale)

    def _change_scale(self, scale):
        self.current_scale = scale
        self.graphicsView.resetTransform()
        real_scale = 1 * (1.2 ** scale)
        self.graphicsView.scale(real_scale, real_scale)

    def set_scene(self, scene):
        self.graphicsView.setScene(scene)