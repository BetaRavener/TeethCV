# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\simplescenewindow.ui'
#
# Created: Sun May 15 00:01:59 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimpleSceneWindow(object):
    def setupUi(self, SimpleSceneWindow):
        SimpleSceneWindow.setObjectName("SimpleSceneWindow")
        SimpleSceneWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(SimpleSceneWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.zoomSlider = QtWidgets.QSlider(self.centralwidget)
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setObjectName("zoomSlider")
        self.verticalLayout.addWidget(self.zoomSlider)
        SimpleSceneWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SimpleSceneWindow)
        QtCore.QMetaObject.connectSlotsByName(SimpleSceneWindow)

    def retranslateUi(self, SimpleSceneWindow):
        _translate = QtCore.QCoreApplication.translate
        SimpleSceneWindow.setWindowTitle(_translate("SimpleSceneWindow", "MainWindow"))

