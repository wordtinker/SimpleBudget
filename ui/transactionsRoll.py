# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'transactionsRoll.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(590, 454)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.rollView = QtWidgets.QTableView(Dialog)
        self.rollView.setObjectName("rollView")
        self.verticalLayout.addWidget(self.rollView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.addTransaction = QtWidgets.QPushButton(Dialog)
        self.addTransaction.setObjectName("addTransaction")
        self.horizontalLayout.addWidget(self.addTransaction)
        self.editTransaction = QtWidgets.QPushButton(Dialog)
        self.editTransaction.setObjectName("editTransaction")
        self.horizontalLayout.addWidget(self.editTransaction)
        self.deleteTransaction = QtWidgets.QPushButton(Dialog)
        self.deleteTransaction.setObjectName("deleteTransaction")
        self.horizontalLayout.addWidget(self.deleteTransaction)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Transaction Roll"))
        self.addTransaction.setText(_translate("Dialog", "Add"))
        self.editTransaction.setText(_translate("Dialog", "Edit"))
        self.deleteTransaction.setText(_translate("Dialog", "Delete"))

