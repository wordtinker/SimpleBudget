from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox
from PyQt5.QtCore import QItemSelectionModel, Qt, QModelIndex

import ui.manageAccounts
from models import AccountsListModel
from enums import ACCOUNT_TYPES


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
