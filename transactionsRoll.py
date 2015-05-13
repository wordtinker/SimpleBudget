from PyQt5.Qt import QDialog, QItemSelectionModel
from PyQt5.QtCore import Qt

from ui.transactionsRoll import Ui_Dialog
from transactionManager import Manager
from models import TableModel
from utils import build_transaction, Category


class TransactionsRoll(Ui_Dialog, QDialog):
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

        # Fetch subcategories list
        subs = self.storage.select_all_subcategories()
        self.categories = dict(((rowid, Category(name, parent, rowid))
                                for name, parent, rowid in subs))
        self.show_transactions()

    def show_transactions(self):
        self.roll.prepare()
        transactions = [build_transaction(t, self.categories)
                        for t in self.storage.select_transactions(self.id)]
        for tr in transactions:
            self.roll.addRow(tr)

    def add_transaction(self):
        manager = Manager(self.categories.values())
        manager.createdTransaction.connect(self.transaction_created)
        manager.exec()

    def edit_transaction(self):
        index = self.selection.currentIndex()
        if index.isValid():
            transaction = index.data(role=Qt.UserRole)
            manager = Manager(self.categories.values(), transaction)
            manager.editedTransaction.connect(self.transaction_edited)
            manager.exec()

    def delete_transaction(self):
        index = self.selection.currentIndex()
        if index.isValid():
            transaction = index.data(role=Qt.UserRole)
            self.storage.delete_transaction(transaction.id, self.id)
            self.roll.removeRows(index.row(), 1)

    def transaction_created(self, date, amount, info, category_id):
        tr = self.storage.\
            add_transaction(date, amount, info, self.id, category_id)
        transaction = build_transaction(tr, self.categories)
        self.roll.addRow(transaction)

    def transaction_edited(self, date, amount, info, category_id, trans_id):
        self.storage.update_transaction(
            trans_id, self.id, date, amount, info, category_id)
        self.show_transactions()