# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\fitterdialog.ui'
#
# Created: Sun Apr 17 02:08:58 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_fitterDialog(object):
    def setupUi(self, fitterDialog):
        fitterDialog.setObjectName("fitterDialog")
        fitterDialog.resize(800, 640)
        self.verticalLayout = QtWidgets.QVBoxLayout(fitterDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.openButton = QtWidgets.QPushButton(fitterDialog)
        self.openButton.setObjectName("openButton")
        self.horizontalLayout_2.addWidget(self.openButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(fitterDialog)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(fitterDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.zoomSlider = QtWidgets.QSlider(fitterDialog)
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setObjectName("zoomSlider")
        self.horizontalLayout_4.addWidget(self.zoomSlider)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.filterButton = QtWidgets.QPushButton(fitterDialog)
        self.filterButton.setObjectName("filterButton")
        self.verticalLayout_2.addWidget(self.filterButton)
        self.detectEdgesButton = QtWidgets.QPushButton(fitterDialog)
        self.detectEdgesButton.setObjectName("detectEdgesButton")
        self.verticalLayout_2.addWidget(self.detectEdgesButton)
        self.animateButton = QtWidgets.QPushButton(fitterDialog)
        self.animateButton.setObjectName("animateButton")
        self.verticalLayout_2.addWidget(self.animateButton)
        self.fitButton = QtWidgets.QPushButton(fitterDialog)
        self.fitButton.setObjectName("fitButton")
        self.verticalLayout_2.addWidget(self.fitButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(fitterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(fitterDialog)
        self.buttonBox.accepted.connect(fitterDialog.accept)
        self.buttonBox.rejected.connect(fitterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(fitterDialog)

    def retranslateUi(self, fitterDialog):
        _translate = QtCore.QCoreApplication.translate
        fitterDialog.setWindowTitle(_translate("fitterDialog", "Dialog"))
        self.openButton.setText(_translate("fitterDialog", "Open"))
        self.label.setText(_translate("fitterDialog", "Zoom"))
        self.filterButton.setText(_translate("fitterDialog", "Filter Image"))
        self.detectEdgesButton.setText(_translate("fitterDialog", "Detect Edges"))
        self.animateButton.setText(_translate("fitterDialog", "Animate"))
        self.fitButton.setText(_translate("fitterDialog", "Fit"))

