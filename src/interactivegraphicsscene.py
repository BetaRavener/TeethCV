from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent


class InteractiveGraphicsScene(QGraphicsScene):
    clicked = pyqtSignal(QGraphicsSceneMouseEvent)

    def __init__(self):
        super(QGraphicsScene, self).__init__()

    def mouseReleaseEvent(self, event):
        self.clicked.emit(event)