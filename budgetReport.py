from PyQt5.Qt import QDialog, QDate, QLabel
from ui.budgetReport import Ui_Dialog
from ui.QBar import QBar
from models import TableModel
from enums import YEARS, MONTHS


class BudgetReport(Ui_Dialog, QDialog):
    def __init__(self, orm):
        super().__init__()
        self.setupUi(self)

        self.orm = orm

        self.set_month_and_year()

        # Connect signals and slots
        self.yearBox.currentTextChanged.connect(
            lambda year: self.load_budget_bars())
        self.monthBox.currentTextChanged.connect(
            lambda month: self.load_budget_bars())

        # Show report for current month as initial
        self.load_budget_bars()

        # Prepare place for transactions list
        self.transactions = TableModel(("Date", "Amount", "Info", "Category"))
        self.transactionsView.setModel(self.transactions)

    def set_month_and_year(self):
        """
        Sets initial values for year and month boxes.
        """
        self.yearBox.addItems(YEARS)
        self.monthBox.addItems(MONTHS)
        current_date = QDate.currentDate()
        self.yearBox.setCurrentText(str(current_date.year()))
        self.monthBox.setCurrentText(MONTHS[current_date.month()])

    def load_budget_bars(self):
        """
        Loads the budget report from DB for chosen month and year and puts
        it into GUI.
        """
        self.clear_bars()

        year = int(self.yearBox.currentText())
        month = int(self.monthBox.currentIndex())  # by position

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
        bar.mousePressed.connect(self.show_transactions)
        self.barsLayout.addWidget(bar, position, 1)

    def show_transactions(self, q_bar):
        self.transactions.prepare()

        year = int(self.yearBox.currentText())
        month = int(self.monthBox.currentIndex())  # by position
        category = q_bar.model.category

        for transaction in self.orm.fetch_transactions_for_month(month, year, category):
            self.transactions.addRow(transaction)
