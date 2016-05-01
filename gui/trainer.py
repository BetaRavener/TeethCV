# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './gui/qt\trainer.ui'
#
# Created: Fri Apr 29 22:50:33 2016
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
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(Trainer)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.choiceSlider = QtWidgets.QSlider(Trainer)
        self.choiceSlider.setOrientation(QtCore.Qt.Horizontal)
        self.choiceSlider.setObjectName("choiceSlider")
        self.horizontalLayout_4.addWidget(self.choiceSlider)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.alignButton = QtWidgets.QPushButton(Trainer)
        self.alignButton.setObjectName("alignButton")
        self.verticalLayout_2.addWidget(self.alignButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(Trainer)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.thresholdSpinBox = QtWidgets.QDoubleSpinBox(Trainer)
        self.thresholdSpinBox.setDecimals(3)
        self.thresholdSpinBox.setMaximum(1.0)
        self.thresholdSpinBox.setSingleStep(0.01)
        self.thresholdSpinBox.setProperty("value", 0.9)
        self.thresholdSpinBox.setObjectName("thresholdSpinBox")
        self.horizontalLayout_3.addWidget(self.thresholdSpinBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
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
        self.label_3.setText(_translate("Trainer", "Tooth"))
        self.alignButton.setText(_translate("Trainer", "Align"))
        self.label_2.setText(_translate("Trainer", "Threshold"))
        self.trainButton.setText(_translate("Trainer", "Train"))
        self.label.setText(_translate("Trainer", "Number of components:"))

