import sys
from PyQt5.QtCore import QUrl, Qt, QObject
from PyQt5.QtGui import QPainter, QColor, QFont, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtQuick import QQuickView, QQuickItem, QQuickPaintedItem
from gui
/


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.text = u'\u041b\u0435\u0432 \u041d\u0438\u043a\u043e\u043b\u0430\
\u0435\u0432\u0438\u0447 \u0422\u043e\u043b\u0441\u0442\u043e\u0439: \n\
\u0410\u043d\u043d\u0430 \u041a\u0430\u0440\u0435\u043d\u0438\u043d\u0430'
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw text')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Decorative', 10))
        qp.drawText(event.rect(), Qt.AlignCenter, self.text)

# Main Function
if __name__ == '__main__':
    # Create main app
    myApp = QApplication(sys.argv)





    ex = Example()

    # Execute the Application and Exit
    sys.exit(myApp.exec_())
