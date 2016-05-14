# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/qt/initposition.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PoseDialog(object):
    def setupUi(self, PoseDialog):
        PoseDialog.setObjectName("PoseDialog")
        PoseDialog.resize(1000, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(PoseDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.openButton = QtWidgets.QPushButton(PoseDialog)
        self.openButton.setObjectName("openButton")
        self.verticalLayout_2.addWidget(self.openButton)
        self.findButton = QtWidgets.QPushButton(PoseDialog)
        self.findButton.setObjectName("findButton")
        self.verticalLayout_2.addWidget(self.findButton)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.graphicsView = QtWidgets.QGraphicsView(PoseDialog)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(PoseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PoseDialog)
        self.buttonBox.accepted.connect(PoseDialog.accept)
        self.buttonBox.rejected.connect(PoseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PoseDialog)

    def retranslateUi(self, PoseDialog):
        _translate = QtCore.QCoreApplication.translate
        PoseDialog.setWindowTitle(_translate("PoseDialog", "Dialog"))
        self.openButton.setText(_translate("PoseDialog", "Open"))
        self.findButton.setText(_translate("PoseDialog", "Find"))

