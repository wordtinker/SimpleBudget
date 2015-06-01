from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtWidgets import QLabel
from ui.QBar import QBar

from models import TreeModel, TreeItem
from ui.mainWindow import Ui_MainWindow

import os
import sys
import logging
from collections import OrderedDict
import datetime

import config
from enums import ACCOUNT_TYPES
from utils import Account, ORM
from accountsManager import AccountsManager
from categoriesManager import CategoriesManager
from transactionsRoll import TransactionsRoll
from budgetManager import BudgetManager
from budgetReport import BudgetReport
from balanceReport import BalanceReport

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
    """
    with open(os.path.join(APP_DATA_PATH, config.RECENT), 'w') as recent:
        recent.write(name)


def order_accounts(accounts):
    """
    Takes a list of accounts and turns it into dictionary with account type keys.
    :param accounts: list of Accounts
    :return: OrderedDict of Accounts
    """
    account_dict = OrderedDict((i, []) for i in ACCOUNT_TYPES)

    for acc in accounts:
        account_dict[acc.type].append(acc)
    return OrderedDict((k, v) for k, v in account_dict.items() if len(v) > 0)


class AccountsTree(TreeModel):
    def __init__(self, orm):
        super().__init__(('Account', 'Balance'))
        self.orm = orm
        self._update_accounts()

    def _update_accounts(self):
        """
        Fetches account list from DB and builds a tree model of accounts.
        Adds subtotal and grand total to that model.
        """
        accounts = self.orm.fetch_accounts_summary()
        account_dict = order_accounts(accounts)

        for key, accs in account_dict.items():
            item = TreeItem((key, ''), self.rootItem)
            self.rootItem.appendChild(item)
            for acc in accs:
                acc_item = TreeItem(acc, item)
                item.appendChild(acc_item)
            # Add type total
            if len(accs) > 1:
                sub_balance = sum(acc.balance for acc in accs if not acc.extotal)
                subtotal = TreeItem(('Total', sub_balance), item)
                item.appendChild(subtotal)

        # Add grand total
        total_balance = sum([acc.balance for acc in accounts if not acc.extotal])
        total = TreeItem(('Grand Total', total_balance), self.rootItem)
        self.rootItem.appendChild(total)


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        self.orm = None
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
        self.actionAbout.triggered.connect(self.show_about)
        self.actionBudgetReport.triggered.connect(self.report_budget)
        self.actionBalance.triggered.connect(self.report_balance)

        self.accountsTree.doubleClicked.connect(self.account_clicked)

        # Try to open the most recent file
        self.load_recent_file()

    def show_accounts(self):
        """
        Reloads the account model into view.
        """
        self.accounts = AccountsTree(self.orm)
        self.accountsTree.setModel(self.accounts)
        self.accountsTree.expandAll()

    def show_budget_report(self):
        """
        Loads the budget report from DB for current month and year and puts
        it into GUI.
        """
        self.clear_bars()

        year = datetime.date.today().year
        month = datetime.date.today().month

        for budget_bar in self.orm.fetch_budget_report_bars(month, year):
            self.add_bar(budget_bar)

        self.barsLayout.setColumnStretch(1, 1)

    def clear_bars(self):
        """
        Clears the widget for budget report.
        """
        for i in reversed(range(self.barsLayout.count())):
            widget = self.barsLayout.itemAt(i).widget()
            # Detach from layout
            self.barsLayout.removeWidget(widget)
            # Remove from GUI
            widget.setParent(None)

    def add_bar(self, budget_bar):
        """
        Adds single bar to the budget report at selected position
        """
        category = budget_bar.category
        category_text = category.parent + '::' + category.name
        position = self.barsLayout.rowCount() + 1
        self.barsLayout.addWidget(QLabel(category_text), position, 0)
        bar = QBar(budget_bar)
        self.barsLayout.addWidget(bar, position, 1)
        self.barsLayout.addWidget(QLabel(budget_bar.expectation), position, 2)

    def load_recent_file(self):
        """
        Tries to find the most recent opened file.
        """
        file_name = ''
        file_path = os.path.join(APP_DATA_PATH, config.RECENT)
        if os.path.exists(file_path):
            with open(file_path, 'r') as recent:
                file_name = recent.readline()

        if file_name and os.path.exists(file_name):
            self.open_file(file_name)

    def choose_file(self):
        """
        Fires up user dialog letting him choose file to be opened.
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(config.FILE_TYPE)
        if dialog.exec():
            file_name = dialog.selectedFiles()[0]
            self.open_file(file_name)

    def create_file(self):
        """
        Fires up user dialog letting him create new file.
        """
        file_name, _ = QFileDialog.getSaveFileName(
            self, caption='Save as...', filter=config.FILE_TYPE)

        if file_name:
            # if file is new file_name comes w/o extension, have to add it
            ext = config.FILE_TYPE.split('*')[1]
            if not file_name.endswith(ext):
                file_name += ext

            self.open_file(file_name)

    def open_file(self, name):
        """
        Opens the DB file.
        """
        # read dbfile and load data
        self.orm = ORM(name)

        self.show_accounts()
        self.show_budget_report()

        # update recent filename
        update_recent(name)

    def close_file(self):
        """
        Closes the DB file and cleans up GUI.
        """
        # Clear the budget report
        self.clear_bars()
        # Clear the accounts tree view
        self.accounts = None
        self.accountsTree.setModel(None)
        # Release DB
        self.orm = None
        # Forget recent filename
        update_recent()

    def exit_action_triggered(self):
        """
        Exits the program.
        """
        self.close()

    def manage_accounts(self):
        """
        Fires up the widget to manage accounts
        """
        if self.orm and self.accounts:

            acc_manager = AccountsManager(self.orm)

            self.menuBar.setEnabled(False)

            acc_manager.exec()

            self.menuBar.setEnabled(True)

            # Update if there was changes
            self.show_accounts()
            self.show_budget_report()

    def manage_categories(self):
        """
        Fires up the widget to manage accounts
        """
        if self.orm and self.accounts:
            cat_manager = CategoriesManager(self.orm)

            self.menuBar.setEnabled(False)

            cat_manager.exec()

            self.menuBar.setEnabled(True)

    def manage_budget(self):
        """
        Fires up the widget to manage budget
        """
        if self.orm and self.accounts:
            budget_manager = BudgetManager(self.orm)

            self.menuBar.setEnabled(False)

            budget_manager.exec()

            self.menuBar.setEnabled(True)
            # Update budget report
            self.show_budget_report()

    def report_budget(self):
        """
        Fires up the widget with budget report.
        """
        if self.orm and self.accounts:
            report = BudgetReport(self.orm)
            self.menuBar.setEnabled(False)
            report.exec()
            self.menuBar.setEnabled(True)

    def report_balance(self):
        """
        Fires up the widget with balance report.
        """
        if self.orm and self.accounts:
            report = BalanceReport(self.orm)
            self.menuBar.setEnabled(False)
            report.exec()
            self.menuBar.setEnabled(True)

    def show_about(self):
        message = " ".join([config.APPNAME, config.VERSION, '\n'])
        message += "Icons are designed by Freepik."
        QMessageBox.information(self, "About",  message)

    def account_clicked(self, index: QModelIndex):
        """
        Opens the list of transactions for given index in the account
        tree model.
        """
        account = index.data(role=Qt.UserRole)
        if not isinstance(account, Account):
            return

        transaction_manager = TransactionsRoll(self.orm, account)

        self.menuBar.setEnabled(False)

        transaction_manager.exec()

        self.menuBar.setEnabled(True)

        # Update if there was changes
        self.show_accounts()
        self.show_budget_report()

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
