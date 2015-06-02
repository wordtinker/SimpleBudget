from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox
from PyQt5.QtCore import QItemSelectionModel, Qt, QModelIndex

import ui.manageAccounts
from models import ListModel
from enums import ACCOUNT_TYPES
from utils import show_warning


class AccountsManager(ui.manageAccounts.Ui_Dialog, QDialog):
    """
    GUI that handles creation, editing and deletion of accounts.
    """
    def __init__(self, orm):
        super().__init__()
        self.setupUi(self)

        self.orm = orm

        self.accounts = ListModel()
        self.accountsView.setModel(self.accounts)

        self.selection = QItemSelectionModel(self.accounts)
        self.accountsView.setSelectionModel(self.selection)

        self.selection.currentRowChanged.connect(self.selection_changed)

        self.typeBox.addItems(ACCOUNT_TYPES)
        self.typeBox.currentTextChanged.connect(self.type_changed)

        self.closedBox.stateChanged.connect(self.closed_changed)
        self.exBudgetBox.stateChanged.connect(self.budget_changed)

        self.addAccountButton.clicked.connect(self.add_account)
        self.deleteAccountButton.clicked.connect(self.delete_account)

        for acc in self.orm.fetch_accounts():
            self.accounts.addItem(acc)

    def selection_changed(self, curr_index: QModelIndex, prev_index: QModelIndex):
        """
        Updates the information about currently selected account.
        """
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

    def type_changed(self, text: str):
        """
        Changes the type of the account in DB and GUI.
        """
        model_indexes = self.selection.selectedIndexes()
        if not model_indexes:
            return None

        model_index = model_indexes[0]
        acc = model_index.data(role=Qt.UserRole)

        # Catch only changes that differ for selected account
        if acc.type != text:
            self.orm.update_account_type(acc, text)
            acc.type = text

    def closed_changed(self, state: int):
        """
        Changes close status of the account in DB and GUI.
        """
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
            self.orm.update_account_status(acc, state)
            acc.closed = state

    def budget_changed(self, state: int):
        """
        Changes the budget status of account in DB and GUI.
        """
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
            self.orm.update_account_budget_status(acc, state)
            acc.exbudget = state

    def add_account(self):
        """
        Creates account with default attributes in DB and adds it to GUI.
        """
        name, ok = QInputDialog.getText(self, "Add new account",
                                        "Enter the name of the new account:")

        if ok and name:
            acc = self.orm.add_account(name)
            self.accounts.addItem(acc)

    def delete_account(self):
        """
        Tries to delete the account from DB, if successful deletes it from GUI.
        """
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
            deletion = self.orm.delete_account(acc)
            if not deletion:
                show_warning("Can't delete account.")
            else:
                self.accounts.removeRow(model_index.row())
