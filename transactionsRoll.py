from PyQt5.Qt import QDialog, QItemSelectionModel
from PyQt5.QtCore import Qt

from ui.transactionsRoll import Ui_Dialog
from transactionManager import Manager
from models import TableModel
from utils import build_transaction, fetch_subcategories


class TransactionsRoll(Ui_Dialog, QDialog):
    """
    GUI that handles the list of all transactions for given account.
    """
    def __init__(self, storage, acc_id):
        super().__init__()
        self.setupUi(self)

        self.storage = storage
        self.id = acc_id

        self.roll = TableModel(("Date", "Amount", "Info", "Category"))
        self.rollView.setModel(self.roll)
        self.selection = QItemSelectionModel(self.roll)
        self.rollView.setSelectionModel(self.selection)

        self.addTransaction.clicked.connect(self.add_transaction)
        self.editTransaction.clicked.connect(self.edit_transaction)
        self.deleteTransaction.clicked.connect(self.delete_transaction)

        self.categories = fetch_subcategories(self.storage)

        self.show_transactions()

    def show_transactions(self):
        """
        Fetches transactions from DB and shows them.
        """
        self.roll.prepare()
        transactions = [build_transaction(t, self.categories)
                        for t in self.storage.select_transactions(self.id)]
        for tr in transactions:
            self.roll.addRow(tr)

    def add_transaction(self):
        """
        Fires up GUI for adding transaction.
        """
        manager = Manager(self.categories.values())
        manager.createdTransaction.connect(self.transaction_created)
        manager.exec()

    def edit_transaction(self):
        """
        Fires up GUI for editing transaction.
        """
        index = self.selection.currentIndex()
        if index.isValid():
            transaction = index.data(role=Qt.UserRole)
            manager = Manager(self.categories.values(), transaction)
            manager.editedTransaction.connect(self.transaction_edited)
            manager.exec()

    def delete_transaction(self):
        """
        Deletes transaction from DB and GUI.
        """
        index = self.selection.currentIndex()
        if index.isValid():
            transaction = index.data(role=Qt.UserRole)
            self.storage.delete_transaction(transaction.id, self.id)
            self.roll.removeRows(index.row(), 1)

    def transaction_created(self, date, amount, info, category_id):
        """
        Catches transaction created signal and adds transaction to DB and GUI.
        """
        tr = self.storage.\
            add_transaction(date, amount, info, self.id, category_id)
        transaction = build_transaction(tr, self.categories)
        self.roll.addRow(transaction)

    def transaction_edited(self, date, amount, info, category_id, trans_id):
        """
        Catches transaction edited signal and updates transaction in the DB,
        redraws all transactions in the GUI.
        """
        self.storage.update_transaction(
            trans_id, self.id, date, amount, info, category_id)
        self.show_transactions()
