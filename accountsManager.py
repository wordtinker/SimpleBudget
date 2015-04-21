from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox
from PyQt5.QtCore import QItemSelectionModel, QAbstractListModel, QVariant, Qt,\
    QModelIndex

import ui.manageAccounts

from enums import ACCOUNT_TYPES, Account


class AccountsListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.items = []

    # Basic methods

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        # User role for returnin full informations about account
        if role == Qt.UserRole:
            return QVariant(self.items[index.row()])

        if role != Qt.DisplayRole:
            return QVariant()

        acc = self.items[index.row()]
        return QVariant(acc.name)

    # Editable model methods

    def setData(self, index, value, role=None):
        if index.isValid():
            self.items[index.row()] = Account(*value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.items.insert(position, None)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.items.pop(position)
        self.endRemoveRows()
        return True

    def addItem(self, item):
        row = 0
        self.insertRows(row, 1)
        self.setData(self.index(row), item)


class AccountsManager(ui.manageAccounts.Ui_Dialog, QDialog):
    def __init__(self, storage):
        super().__init__()
        self.setupUi(self)

        self.storage = storage

        self.accounts = AccountsListModel()
        self.accountsView.setModel(self.accounts)

        self.selection = QItemSelectionModel(self.accounts)
        self.accountsView.setSelectionModel(self.selection)

        self.selection.currentRowChanged.connect(self.selection_changed)

        self.typeBox.addItems(ACCOUNT_TYPES)
        self.typeBox.currentTextChanged.connect(self.type_changed)

        self.closedBox.stateChanged.connect(self.closed_changed)
        self.exBudgetBox.stateChanged.connect(self.budget_changed)
        self.exTotalBox.stateChanged.connect(self.total_changed)

        self.addAccountButton.clicked.connect(self.add_account)
        self.deleteAccountButton.clicked.connect(self.delete_account)

        for acc in self.storage.select_accounts():
            self.accounts.addItem(acc)

    def selection_changed(self, curr_index: QModelIndex, prev_index: QModelIndex):
        if not curr_index.isValid():
            return None

        # Make sure selection is visible in the view
        self.selection.setCurrentIndex(
            curr_index, QItemSelectionModel.SelectCurrent)

        acc = curr_index.data(role=Qt.UserRole)

        # Set the type of account
        self.typeBox.setCurrentText(acc.type)

        # Set the checkboxes
        self.closedBox.setChecked(acc.closed)
        self.exBudgetBox.setChecked(acc.exbudget)
        self.exTotalBox.setChecked(acc.extotal)

    def type_changed(self, text: str):
        model_indexes = self.selection.selectedIndexes()
        if not model_indexes:
            return None

        model_index = model_indexes[0]
        acc = model_index.data(role=Qt.UserRole)

        # Catch only changes that differ for selected account
        if acc.type != text:
            self.storage.update_account_type(acc.id, text)
            acc.type = text

    def closed_changed(self, state: int):
        model_indexes = self.selection.selectedIndexes()
        if not model_indexes:
            return None

        model_index = model_indexes[0]
        acc = model_index.data(role=Qt.UserRole)

        # Catch only changes that differ for selected account
        # acc states in (0,1); Qt.CheckState in (0,1,2)
        # (0,1,2)//2 -> (0,0,1)
        state //= 2
        if acc.closed != state:
            self.storage.update_account_status(acc.id, state)
            acc.closed = state

    def budget_changed(self, state: int):
        model_indexes = self.selection.selectedIndexes()
        if not model_indexes:
            return None

        model_index = model_indexes[0]
        acc = model_index.data(role=Qt.UserRole)

        # Catch only changes that differ for selected account
        # acc states in (0,1); Qt.CheckState in (0,1,2)
        # (0,1,2)//2 -> (0,0,1)
        state //= 2
        if acc.exbudget != state:
            self.storage.update_account_budget_status(acc.id, state)
            acc.exbudget = state

    def total_changed(self, state: int):
        model_indexes = self.selection.selectedIndexes()
        if not model_indexes:
            return None

        model_index = model_indexes[0]
        acc = model_index.data(role=Qt.UserRole)

        # Catch only changes that differ for selected account
        # acc states in (0,1); Qt.CheckState in (0,1,2)
        # (0,1,2)//2 -> (0,0,1)
        state //= 2
        if acc.extotal != state:
            self.storage.update_account_total_status(acc.id, state)
            acc.extotal = state

    def add_account(self):
        name, ok = QInputDialog.getText(self, "Add new account",
                "Enter the name of the new account:")

        if ok and name:
            acc = self.storage.add_account(name)
            self.accounts.addItem(acc)

    def delete_account(self):
        model_indexes = self.selection.selectedIndexes()
        if not model_indexes:  # the list of accounts is empty
            return None

        model_index = model_indexes[0]
        acc = model_index.data(role=Qt.UserRole)

        msgBox = QMessageBox()
        msgBox.setText("Delete the {} account?".format(acc.name))
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()

        if ret == QMessageBox.Ok:
            self.storage.delete_account(acc.id)
            self.accounts.removeRow(model_index.row())
