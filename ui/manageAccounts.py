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
        Dialog.resize(424, 549)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.accountsView = QtWidgets.QListView(Dialog)
        self.accountsView.setMaximumSize(QtCore.QSize(300, 16777215))
        self.accountsView.setObjectName("accountsView")
        self.verticalLayout_2.addWidget(self.accountsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addAccountButton = QtWidgets.QPushButton(Dialog)
        self.addAccountButton.setObjectName("addAccountButton")
        self.horizontalLayout.addWidget(self.addAccountButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.deleteAccountButton = QtWidgets.QPushButton(Dialog)
        self.deleteAccountButton.setObjectName("deleteAccountButton")
        self.horizontalLayout.addWidget(self.deleteAccountButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.typeBox = QtWidgets.QComboBox(Dialog)
        self.typeBox.setObjectName("typeBox")
        self.horizontalLayout_2.addWidget(self.typeBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.closedBox = QtWidgets.QCheckBox(Dialog)
        self.closedBox.setObjectName("closedBox")
        self.verticalLayout.addWidget(self.closedBox)
        self.exBudgetBox = QtWidgets.QCheckBox(Dialog)
        self.exBudgetBox.setObjectName("exBudgetBox")
        self.verticalLayout.addWidget(self.exBudgetBox)
        self.exTotalBox = QtWidgets.QCheckBox(Dialog)
        self.exTotalBox.setObjectName("exTotalBox")
        self.verticalLayout.addWidget(self.exTotalBox)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.horizontalLayout_4.setStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Accounts"))
        self.addAccountButton.setText(_translate("Dialog", "Add"))
        self.deleteAccountButton.setText(_translate("Dialog", "Delete"))
        self.label.setText(_translate("Dialog", "Type"))
        self.closedBox.setText(_translate("Dialog", "closed"))
        self.exBudgetBox.setText(_translate("Dialog", "exclude from budget"))
        self.exTotalBox.setText(_translate("Dialog", "eclude from grand total"))

