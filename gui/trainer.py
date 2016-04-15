# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\trainer.ui'
#
# Created: Fri Apr 15 22:45:30 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Trainer(object):
    def setupUi(self, Trainer):
        Trainer.setObjectName("Trainer")
        Trainer.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Trainer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.graphicsView = QtWidgets.QGraphicsView(Trainer)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout_2.addWidget(self.graphicsView)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.choiceSlider = QtWidgets.QSlider(Trainer)
        self.choiceSlider.setOrientation(QtCore.Qt.Horizontal)
        self.choiceSlider.setObjectName("choiceSlider")
        self.verticalLayout_2.addWidget(self.choiceSlider)
        self.alignButton = QtWidgets.QPushButton(Trainer)
        self.alignButton.setObjectName("alignButton")
        self.verticalLayout_2.addWidget(self.alignButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.trainButton = QtWidgets.QPushButton(Trainer)
        self.trainButton.setObjectName("trainButton")
        self.verticalLayout_2.addWidget(self.trainButton)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Trainer)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.compCountLabel = QtWidgets.QLabel(Trainer)
        self.compCountLabel.setText("")
        self.compCountLabel.setObjectName("compCountLabel")
        self.horizontalLayout.addWidget(self.compCountLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Trainer)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Trainer)
        self.buttonBox.accepted.connect(Trainer.accept)
        self.buttonBox.rejected.connect(Trainer.reject)
        QtCore.QMetaObject.connectSlotsByName(Trainer)

    def retranslateUi(self, Trainer):
        _translate = QtCore.QCoreApplication.translate
        Trainer.setWindowTitle(_translate("Trainer", "Dialog"))
        self.alignButton.setText(_translate("Trainer", "Align"))
        self.trainButton.setText(_translate("Trainer", "Train"))
        self.label.setText(_translate("Trainer", "Number of components:"))

