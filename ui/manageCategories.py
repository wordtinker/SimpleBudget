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
        Dialog.resize(403, 301)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.categoriesView = QtWidgets.QTreeView(Dialog)
        self.categoriesView.setObjectName("categoriesView")
        self.verticalLayout_2.addWidget(self.categoriesView)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.caregoryName = QtWidgets.QLineEdit(Dialog)
        self.caregoryName.setObjectName("caregoryName")
        self.verticalLayout.addWidget(self.caregoryName)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.categoryParent = QtWidgets.QComboBox(Dialog)
        self.categoryParent.setObjectName("categoryParent")
        self.verticalLayout.addWidget(self.categoryParent)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.addBtn = QtWidgets.QPushButton(Dialog)
        self.addBtn.setObjectName("addBtn")
        self.verticalLayout.addWidget(self.addBtn)
        self.deleteBtn = QtWidgets.QPushButton(Dialog)
        self.deleteBtn.setObjectName("deleteBtn")
        self.verticalLayout.addWidget(self.deleteBtn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Categories"))
        self.label_2.setText(_translate("Dialog", "Name"))
        self.label.setText(_translate("Dialog", "Parent"))
        self.addBtn.setText(_translate("Dialog", "Add"))
        self.deleteBtn.setText(_translate("Dialog", "Delete"))

