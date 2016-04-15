import random
from time import sleep

import math
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QRectF
from PyQt5.QtGui import QImage, QColor, QPainter, QPainterPath, QPixmap, QPen, QBrush
from PyQt5.QtWidgets import QDialog, QGraphicsScene, QFileDialog, QGraphicsSceneMouseEvent

from gui.fitterdialog import Ui_fitterDialog
from src.datamanager import DataManager
from src.interactivegraphicsscene import InteractiveGraphicsScene
from src.radiograph import Radiograph
from src.utils import toQImage


class Animator(QThread):
    output_signal = pyqtSignal(QImage)
    exiting = False
    stars = None
    width = None
    height = None

    def __init__(self):
        super(Animator, self).__init__()

    def __del__(self):
        # Notify worker that it's being destroyed so it can stop
        self.stop()

    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.

        random.seed()
        n = self.stars

        while not self.exiting and n > 0:
            image = QImage(self.width, self.height,
                           QImage.Format_ARGB32)
            image.fill(QColor.fromRgb(0, 0, 0, 0))

            painter = QPainter()
            painter.begin(image)
            painter.setPen(QPen(QColor.fromRgb(255, 0, 0)))
            #TODO: The active shape model should have a function "make step"
            #TODO: so that this one can animate the steps
            painter.drawLine(0, n, self.width, self.height)
            painter.end()

            self.output_signal.emit(image)
            n -= 1
            sleep(0.1)

    def render(self, size, stars):
        self.width, self.height = size
        self.stars = stars
        self.start()

    def stop(self):
        self.exiting = True
        self.wait()


class FitterDialog(QDialog, Ui_fitterDialog):
    scene = None
    animator = None
    data_manager = None
    current_scale = 0
    animation_overlay = None
    indicator_position = None
    indicator = None
    radiograph = None

    def __init__(self, data_manager):
        super(FitterDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        assert isinstance(data_manager, DataManager)
        self.data_manager = data_manager

        self.scene = InteractiveGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.scene.clicked.connect(self._set_indicator)

        self.radiograph = self.data_manager.radiographs[0]
        self.display_radiograph()

        self.openButton.clicked.connect(self._open_radiograph)

        self.zoomSlider.setMinimum(-10)
        self.zoomSlider.setMaximum(10)
        self.zoomSlider.setValue(self.current_scale)
        self.zoomSlider.valueChanged.connect(self.change_scale)

        self.animateButton.clicked.connect(self._animator_entry)

    def _open_radiograph(self):
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory("./data/Radiographs")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Radiograph (*.tif)")
        if file_dialog.exec_() and len(file_dialog.selectedFiles()) == 1:
            self.radiograph = Radiograph()
            self.radiograph.path_to_img = file_dialog.selectedFiles()[0]
            self.display_radiograph()

    def change_scale(self, scale):
        self.current_scale = scale
        self.graphicsView.resetTransform()
        real_scale = 1 + scale * (0.1 if scale >= 0 else 0.05)
        self.graphicsView.scale(real_scale, real_scale)

    def _set_indicator(self, mouse_event):
        assert isinstance(mouse_event, QGraphicsSceneMouseEvent)
        pos = mouse_event.scenePos()
        self.indicator_position = (pos.x(), pos.y())
        self._redraw_indicator()

    def _redraw_indicator(self):
        if self.indicator is not None:
            self.scene.removeItem(self.indicator)

        self.indicator = self.scene.addEllipse(self.indicator_position[0] - 5, self.indicator_position[1] - 5,
                                               10, 10,
                                               pen=QPen(QColor.fromRgb(255, 0, 0)),
                                               brush=QBrush(QColor.fromRgb(255, 0, 0)))
        self.scene.update()

    def _animator_entry(self):
        if self.animator is None:
            self._animation_start()
        else:
            self.animator.stop()

    def _animation_start(self):
        self._disable_ui()

        self.animator = Animator()
        self.animator.finished.connect(self._animator_end)
        self.animator.output_signal.connect(self._update_image)

        self.animator.render((self.scene.width(), self.scene.height()), 100)

    def _animator_end(self):
        self.animateButton.setText("Animate")
        self.animator = None

    def _disable_ui(self):
        self.animateButton.setText("Stop")

    def _update_image(self, image):
        if self.animation_overlay is not None:
            self.scene.removeItem(self.animation_overlay)

        pixmap = QPixmap()
        pixmap = pixmap.fromImage(image)
        self.animation_overlay = self.scene.addPixmap(pixmap)
        self.animation_overlay.setPos(0, 0)
        self.scene.update()

    def _focus_view(self):
        rect = self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)
        self.graphicsView.fitInView(rect, Qt.KeepAspectRatio)

    def display_radiograph(self):
        self.scene.clear()
        self.animation_overlay = None
        self.indicator_position = None
        self.indicator = None

        # Load and draw image
        img = toQImage(self.radiograph.image)
        self.scene.addPixmap(QPixmap.fromImage(img))

        # Set generated scene into the view
        self.graphicsView.resetTransform()
        self.graphicsView.centerOn(self.scene.width() / 2, self.scene.height() / 2)
        self.current_scale = 0
        self.zoomSlider.setValue(0)
