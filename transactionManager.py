from PyQt5.Qt import QDialog, pyqtSignal, QDate, Qt
from ui.manageTransaction import Ui_manageTransaction
import datetime
from models import CategoryListModel


class Manager(Ui_manageTransaction, QDialog):

    # Date, amount, info, category_id
    createdTransaction = pyqtSignal(datetime.date, int, str, int)
    # Date, amount, info, category_id, transaction_id
    editedTransaction = pyqtSignal(datetime.date, int, str, int, int)

    def __init__(self, categories, transaction=None):
        super().__init__()
        self.setupUi(self)

        self.categories = categories
        self.transaction = transaction
        # List all categories
        self.categories_model = CategoryListModel()
        for cat in self.categories:
            self.categories_model.addItem(cat)
        self.categorysBox.setModel(self.categories_model)

        if self.transaction:
            y, m, d = self.transaction.date.split('-')
            self.dateEdit.setDate(QDate(int(y), int(m), int(d)))
            self.amountBox.setValue(self.transaction.amount)
            self.infoEdit.setText(self.transaction.info)
            self.categorysBox.setCurrentText(self.transaction.category)
        else:
            today = QDate.currentDate()
            self.dateEdit.setDate(today)

    def accept(self):
        if self.is_valid():
            date = self.dateEdit.date().toPyDate()
            amount = int(self.amountBox.value() * 100)  # to cents
            info = self.infoEdit.text()
            category_id = self.categorysBox.currentData(role=Qt.UserRole).id
            if self.transaction is None:
                self.createdTransaction.emit(date, amount, info, category_id)
            else:
                self.editedTransaction\
                    .emit(date, amount, info, category_id, self.transaction.id)
            QDialog.accept(self)

    def is_valid(self):
        return self.dateEdit.date().isValid()