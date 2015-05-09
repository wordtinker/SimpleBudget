# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageCategories.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.categoriesView = QtWidgets.QTreeView(Dialog)
        self.categoriesView.setGeometry(QtCore.QRect(10, 10, 191, 271))
        self.categoriesView.setObjectName("categoriesView")
        self.addBtn = QtWidgets.QPushButton(Dialog)
        self.addBtn.setGeometry(QtCore.QRect(260, 130, 75, 23))
        self.addBtn.setObjectName("addBtn")
        self.deleteBtn = QtWidgets.QPushButton(Dialog)
        self.deleteBtn.setGeometry(QtCore.QRect(260, 170, 75, 23))
        self.deleteBtn.setObjectName("deleteBtn")
        self.caregoryName = QtWidgets.QLineEdit(Dialog)
        self.caregoryName.setGeometry(QtCore.QRect(220, 10, 113, 20))
        self.caregoryName.setObjectName("caregoryName")
        self.categoryParent = QtWidgets.QComboBox(Dialog)
        self.categoryParent.setGeometry(QtCore.QRect(218, 50, 111, 22))
        self.categoryParent.setObjectName("categoryParent")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.addBtn.setText(_translate("Dialog", "Add"))
        self.deleteBtn.setText(_translate("Dialog", "Delete"))

