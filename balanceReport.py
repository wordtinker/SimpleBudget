from PyQt5.Qt import QDialog, QDate
from ui.balanceReport import Ui_Dialog
from models import TableModel
from enums import YEARS, MONTHS


class BalanceReport(Ui_Dialog, QDialog):
    def __init__(self, orm):
        super().__init__()
        self.setupUi(self)

        self.orm = orm

        self.set_month_and_year()

        # Connect signals and slots
        self.yearBox.currentTextChanged.connect(
            lambda year: self.load_balance())
        self.monthBox.currentTextChanged.connect(
            lambda month: self.load_balance())

        self.roll = TableModel(("Date", "Change", "Total", "Origin", "Category"))
        self.balanceView.setModel(self.roll)

        # Show report for current month as initial
        self.load_balance()

    def set_month_and_year(self):
        """
        Sets initial values for year and month boxes.
        """
        self.yearBox.addItems(YEARS)
        self.monthBox.addItems(MONTHS)
        current_date = QDate.currentDate()
        self.yearBox.setCurrentText(str(current_date.year()))
        self.monthBox.setCurrentText(MONTHS[current_date.month()])

    def load_balance(self):
        """
        Fetches info from ORM and puts it into balance report.
        """
        self.roll.prepare()

        year = int(self.yearBox.currentText())
        month = int(self.monthBox.currentIndex())  # by position

        # Get starting balance active, period -1 day  # TODO including prediction before that
        last_date, balance = self.orm.fetch_balance_to_date(month, year)
        self.roll.addRow((last_date, 0, balance, 'Transaction', "- - -"))

        # Get transaction for the active period
        for transaction in self.orm.fetch_transactions_for_period(month, year):
            balance += transaction.amount
            last_date = max(last_date, transaction.date)
            self.roll.addRow((transaction.date, transaction.amount, balance,
                              'Transaction', transaction.category))

        # Get budget spendings/incoms after active period
        for prediction in\
                self.orm.fetch_budget_prediction(month, year, last_date):
            category = prediction.category
            balance += prediction.amount
            self.roll.addRow((prediction.date, prediction.amount, balance,
                              'Budget', category.parent+"::"+category.name))
