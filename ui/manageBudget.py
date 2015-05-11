# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageBudget.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(837, 451)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.monthBox = QtWidgets.QComboBox(Dialog)
        self.monthBox.setObjectName("monthBox")
        self.horizontalLayout_2.addWidget(self.monthBox)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.yearBox = QtWidgets.QComboBox(Dialog)
        self.yearBox.setObjectName("yearBox")
        self.horizontalLayout_2.addWidget(self.yearBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.recordsView = QtWidgets.QTableView(Dialog)
        self.recordsView.setObjectName("recordsView")
        self.verticalLayout.addWidget(self.recordsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.addBtn = QtWidgets.QPushButton(Dialog)
        self.addBtn.setObjectName("addBtn")
        self.horizontalLayout.addWidget(self.addBtn)
        self.editBtn = QtWidgets.QPushButton(Dialog)
        self.editBtn.setObjectName("editBtn")
        self.horizontalLayout.addWidget(self.editBtn)
        self.deleteBtn = QtWidgets.QPushButton(Dialog)
        self.deleteBtn.setObjectName("deleteBtn")
        self.horizontalLayout.addWidget(self.deleteBtn)
        self.copyBtn = QtWidgets.QPushButton(Dialog)
        self.copyBtn.setObjectName("copyBtn")
        self.horizontalLayout.addWidget(self.copyBtn)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Budget"))
        self.label_2.setText(_translate("Dialog", "Month"))
        self.label.setText(_translate("Dialog", "Year"))
        self.addBtn.setText(_translate("Dialog", "Add"))
        self.editBtn.setText(_translate("Dialog", "Edit"))
        self.deleteBtn.setText(_translate("Dialog", "Delete"))
        self.copyBtn.setText(_translate("Dialog", "Copy from ..."))

