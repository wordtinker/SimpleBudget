# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageAccounts.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(792, 549)
        self.accountsView = QtWidgets.QListView(Dialog)
        self.accountsView.setGeometry(QtCore.QRect(10, 10, 211, 371))
        self.accountsView.setObjectName("accountsView")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 390, 211, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addAccountButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.addAccountButton.setObjectName("addAccountButton")
        self.horizontalLayout.addWidget(self.addAccountButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.deleteAccountButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.deleteAccountButton.setObjectName("deleteAccountButton")
        self.horizontalLayout.addWidget(self.deleteAccountButton)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(290, 30, 47, 13))
        self.label.setObjectName("label")
        self.typeBox = QtWidgets.QComboBox(Dialog)
        self.typeBox.setGeometry(QtCore.QRect(330, 30, 69, 22))
        self.typeBox.setObjectName("typeBox")
        self.closedBox = QtWidgets.QCheckBox(Dialog)
        self.closedBox.setGeometry(QtCore.QRect(290, 60, 70, 17))
        self.closedBox.setObjectName("closedBox")
        self.exBudgetBox = QtWidgets.QCheckBox(Dialog)
        self.exBudgetBox.setGeometry(QtCore.QRect(290, 90, 131, 17))
        self.exBudgetBox.setObjectName("exBudgetBox")
        self.exTotalBox = QtWidgets.QCheckBox(Dialog)
        self.exTotalBox.setGeometry(QtCore.QRect(290, 120, 141, 17))
        self.exTotalBox.setObjectName("exTotalBox")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.addAccountButton.setText(_translate("Dialog", "Add"))
        self.deleteAccountButton.setText(_translate("Dialog", "Delete"))
        self.label.setText(_translate("Dialog", "Type"))
        self.closedBox.setText(_translate("Dialog", "closed"))
        self.exBudgetBox.setText(_translate("Dialog", "exclude from budget"))
        self.exTotalBox.setText(_translate("Dialog", "eclude from grand total"))

