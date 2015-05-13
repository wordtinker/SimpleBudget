from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QModelIndex, Qt

from models import TreeModel, TreeItem
from ui.mainWindow import Ui_MainWindow

import os
import sys
import logging

import config
from enums import ACCOUNT_TYPES, Account
from storage import Storage
from accountsManager import AccountsManager
from categoriesManager import CategoriesManager
from transactionsRoll import TransactionsRoll
from budgetManager import BudgetManager

# Define working directory for app
if "APPDATA" in os.environ:  # We are on Windows
    APP_DATA_PATH = os.path.join(os.environ["APPDATA"], config.APPNAME)
elif "HOME" in os.environ:  # We are on Linux
    APP_DATA_PATH = os.path.join(os.environ["HOME"], "." + config.APPNAME)
else:  # Fallback to our working dir
    APP_DATA_PATH = os.getcwd()


def update_recent(name=''):
    """
    Updates the value of most recent opened file.
    :param name: file name
    :return:
    """
    with open(os.path.join(APP_DATA_PATH, config.RECENT), 'w') as recent:
        recent.write(name)


class AccountsTree(TreeModel):
    def __init__(self, storage):
        super().__init__(('Account', '', 'Balance', '', '', '', ''))
        self.storage = storage
        self._update_accounts()

    def _update_accounts(self):
        accounts = [Account(*a) for a in self.storage.select_accounts_summary()]
        account_dict = dict((i, []) for i in ACCOUNT_TYPES)  # FIXME order

        for acc in accounts:
            acc.balance /= 100  # from cents
            account_dict[acc.type].append(acc)
        account_dict = {k: v for k, v in account_dict.items() if len(v) > 0}

        for key, accs in account_dict.items():
            item = TreeItem((key, '', '', '', '', '', ''), self.rootItem)
            self.rootItem.appendChild(item)
            for acc in accs:
                acc_item = TreeItem(acc, item)
                item.appendChild(acc_item)
            # Add type total
            if len(accs) > 1:
                sub_balance = sum(acc.balance for acc in accs if not acc.extotal)
                subtotal = TreeItem(('Total', '', sub_balance, '', '', '', ''), item)
                item.appendChild(subtotal)

        # Add grand total
        total_balance = sum([acc.balance for acc in accounts if not acc.extotal])
        total = TreeItem(('Grand Total', '', total_balance, '', '', '', ''), self.rootItem)
        self.rootItem.appendChild(total)


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        self.storage = None
        self.accounts = None

        # Set up the user interface
        self.setupUi(self)

        # Set up some visual tweaks
        self.setObjectName(config.APPNAME)

        # Connect signals and slots
        self.actionOpenFile.triggered.connect(self.choose_file)
        self.actionNewFile.triggered.connect(self.create_file)
        self.actionCloseFile.triggered.connect(self.close_file)
        self.actionQuit.triggered.connect(self.exit_action_triggered)
        self.actionManageAccounts.triggered.connect(self.manage_accounts)
        self.actionManageCategories.triggered.connect(self.manage_categories)
        self.actionBudget.triggered.connect(self.manage_budget)

        self.accountsTree.doubleClicked.connect(self.account_clicked)

        # Try to open the most recent file
        self.load_recent_file()

    def load_recent_file(self):
        file_name = ''
        file_path = os.path.join(APP_DATA_PATH, config.RECENT)
        if os.path.exists(file_path):
            with open(file_path, 'r') as recent:
                file_name = recent.readline()

        if file_name and os.path.exists(file_name):
            self.open_file(file_name)

    def choose_file(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(config.FILE_TYPE)
        if dialog.exec():
            file_name = dialog.selectedFiles()[0]
            self.open_file(file_name)

    def create_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, caption='Save as...', filter=config.FILE_TYPE)

        if file_name:
            # if file is new file_name comes w/o extension, have to add it
            ext = config.FILE_TYPE.split('*')[1]
            if not file_name.endswith(ext):
                file_name += ext

            self.open_file(file_name)

    def open_file(self, name):
        # read dbfile and load data
        self.storage = Storage(name)

        self.show_accounts()

        # update recent filename
        update_recent(name)

    def close_file(self):
        # Clear the accounts tree view
        self.accounts = None
        self.accountsTree.setModel(None)
        # Release storage
        self.storage = None
        # Forget recent filename
        update_recent()

    def exit_action_triggered(self):
        self.close()

    def manage_accounts(self):
        """
        Fires up the widget to manage accounts
        """
        if self.storage and self.accounts:

            acc_manager = AccountsManager(self.storage)

            self.menuBar.setEnabled(False)

            acc_manager.exec()

            self.menuBar.setEnabled(True)

            # Update if there was changes
            self.show_accounts()

    def manage_categories(self):
        """
        Fires up the widget to manage accounts
        """
        if self.storage and self.accounts:
            cat_manager = CategoriesManager(self.storage)

            self.menuBar.setEnabled(False)

            cat_manager.exec()

            self.menuBar.setEnabled(True)

    def manage_budget(self):
        """
        Fires up the widget to manage budget
        """
        if self.storage and self.accounts:
            budget_manager = BudgetManager(self.storage)

            self.menuBar.setEnabled(False)

            budget_manager.exec()

            self.menuBar.setEnabled(True)
            # Update budget report
            # TODO

    def show_accounts(self):
        self.accounts = AccountsTree(self.storage)
        self.accountsTree.setModel(self.accounts)
        self.accountsTree.hideColumn(1)
        self.accountsTree.hideColumn(3)
        self.accountsTree.hideColumn(4)
        self.accountsTree.hideColumn(5)
        self.accountsTree.hideColumn(6)
        self.accountsTree.expandAll()

    def account_clicked(self, index: QModelIndex):
        acc = index.data(role=Qt.UserRole)
        if type(acc) != Account:
            return

        transaction_manager = TransactionsRoll(self.storage, acc.id)

        self.menuBar.setEnabled(False)

        transaction_manager.exec()

        self.menuBar.setEnabled(True)

        # Update if there was changes
        self.show_accounts()

if __name__ == '__main__':
    # Ensure consistency of data dir
    if not os.path.exists(APP_DATA_PATH):
        os.makedirs(APP_DATA_PATH)

    if not os.path.exists(os.path.join(APP_DATA_PATH, config.RECENT)):
        update_recent()

    log_name = os.path.join(APP_DATA_PATH, config.LOG)

    logging.basicConfig(
        filename=log_name,
        format='%(asctime)s %(message)s',
        level=logging.ERROR)
        # level=logging.INFO)
    logging.info("app_data_path:" + APP_DATA_PATH)

    try:
        app = QApplication(sys.argv)

        form = MainWindow()

        form.show()

        sys.exit(app.exec())

    except Exception as e:
        logging.exception(e)
