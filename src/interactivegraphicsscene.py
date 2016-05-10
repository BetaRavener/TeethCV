from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent

__author__ = "Ivan Sevcik"

class InteractiveGraphicsScene(QGraphicsScene):
    clicked = pyqtSignal(QGraphicsSceneMouseEvent)
    enabled = None

    def __init__(self):
        super(QGraphicsScene, self).__init__()
        self.enabled = True

    def mouseReleaseEvent(self, event):
        if self.enabled:
            self.clicked.emit(event)

    def setEnabled(self, enabled):
        self.enabled = enabled
