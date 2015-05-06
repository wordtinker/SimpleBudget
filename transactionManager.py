from PyQt5.Qt import QDialog, pyqtSignal, QDate
from ui.manageTransaction import Ui_manageTransaction
import datetime


class Manager(Ui_manageTransaction, QDialog):

    # Date, amount, info, category id
    createdTransaction = pyqtSignal(datetime.date, int, str, int)
    # Date, amount, info, category id, transaction_id
    editedTransaction = pyqtSignal(datetime.date, int, str, int, int)

    def __init__(self, transaction=None):
        super().__init__()
        self.setupUi(self)

        self.transaction = transaction
        if self.transaction:
            y, m, d = self.transaction.date.split('-')
            self.dateEdit.setDate(QDate(int(y), int(m), int(d)))
            self.amountBox.setValue(self.transaction.amount)
            self.infoEdit.setText(self.transaction.info)
            # TODO category, what if it doesn't match the current list?
        else:
            today = QDate.currentDate()
            self.dateEdit.setDate(today)

    def accept(self):
        if self.is_valid():
            date = self.dateEdit.date().toPyDate()
            amount = int(self.amountBox.value() * 100)  # to cents
            info = self.infoEdit.text()
            category_id = 0  # TODO Category
            if self.transaction is None:
                self.createdTransaction.emit(date, amount, info, category_id)
            else:
                self.editedTransaction\
                    .emit(date, amount, info, category_id, self.transaction.id)
            QDialog.accept(self)
            return

    def is_valid(self):
        return self.dateEdit.date().isValid()