# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\pcavisualizer.ui'
#
# Created: Sat May 14 23:43:40 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PcaVisualizerDialog(object):
    def setupUi(self, PcaVisualizerDialog):
        PcaVisualizerDialog.setObjectName("PcaVisualizerDialog")
        PcaVisualizerDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(PcaVisualizerDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(PcaVisualizerDialog)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, 0, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(PcaVisualizerDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.scrollArea = QtWidgets.QScrollArea(PcaVisualizerDialog)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 118, 167))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.resetButton = QtWidgets.QPushButton(PcaVisualizerDialog)
        self.resetButton.setObjectName("resetButton")
        self.verticalLayout_3.addWidget(self.resetButton)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(PcaVisualizerDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.choiceSlider = QtWidgets.QSlider(PcaVisualizerDialog)
        self.choiceSlider.setOrientation(QtCore.Qt.Horizontal)
        self.choiceSlider.setObjectName("choiceSlider")
        self.horizontalLayout_2.addWidget(self.choiceSlider)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(PcaVisualizerDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PcaVisualizerDialog)
        self.buttonBox.accepted.connect(PcaVisualizerDialog.accept)
        self.buttonBox.rejected.connect(PcaVisualizerDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PcaVisualizerDialog)

    def retranslateUi(self, PcaVisualizerDialog):
        _translate = QtCore.QCoreApplication.translate
        PcaVisualizerDialog.setWindowTitle(_translate("PcaVisualizerDialog", "Dialog"))
        self.label_2.setText(_translate("PcaVisualizerDialog", "Reconstruction params:"))
        self.resetButton.setText(_translate("PcaVisualizerDialog", "Reset"))
        self.label.setText(_translate("PcaVisualizerDialog", "Project"))

