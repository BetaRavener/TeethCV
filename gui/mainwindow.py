# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\mainwindow.ui'
#
# Created: Fri Apr 15 22:45:30 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.radiographSlider = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiographSlider.sizePolicy().hasHeightForWidth())
        self.radiographSlider.setSizePolicy(sizePolicy)
        self.radiographSlider.setMinimumSize(QtCore.QSize(200, 0))
        self.radiographSlider.setOrientation(QtCore.Qt.Horizontal)
        self.radiographSlider.setObjectName("radiographSlider")
        self.verticalLayout.addWidget(self.radiographSlider)
        self.zoomSlider = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoomSlider.sizePolicy().hasHeightForWidth())
        self.zoomSlider.setSizePolicy(sizePolicy)
        self.zoomSlider.setMinimumSize(QtCore.QSize(200, 0))
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setObjectName("zoomSlider")
        self.verticalLayout.addWidget(self.zoomSlider)
        self.trainerButton = QtWidgets.QPushButton(self.centralwidget)
        self.trainerButton.setObjectName("trainerButton")
        self.verticalLayout.addWidget(self.trainerButton)
        self.pcaVisualizerButton = QtWidgets.QPushButton(self.centralwidget)
        self.pcaVisualizerButton.setObjectName("pcaVisualizerButton")
        self.verticalLayout.addWidget(self.pcaVisualizerButton)
        self.fitterButton = QtWidgets.QPushButton(self.centralwidget)
        self.fitterButton.setObjectName("fitterButton")
        self.verticalLayout.addWidget(self.fitterButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.trainerButton.setText(_translate("MainWindow", "Trainer"))
        self.pcaVisualizerButton.setText(_translate("MainWindow", "PCA Visualizer"))
        self.fitterButton.setText(_translate("MainWindow", "Fitter"))

