from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import QDate, QItemSelectionModel, Qt

import ui.manageBudget
from recordManager import Manager
from models import TableModel
from enums import YEARS, MONTHS
from utils import show_warning


class BudgetManager(ui.manageBudget.Ui_Dialog, QDialog):
    """
    GUI that handles creation, editing and deletion of budgets.
    """
    def __init__(self, orm):
        super().__init__()
        self.setupUi(self)

        self.orm = orm

        # Fetch subcategories list
        self.categories = self.orm.fetch_subcategories(full=False)

        self.set_month_and_year()
        self.setup_table()
        self.load_budget_records()

        # Connect signals and slots
        self.yearBox.currentTextChanged.connect(
            lambda year: self.load_budget_records())
        self.monthBox.currentTextChanged.connect(
            lambda month: self.load_budget_records())
        self.addBtn.clicked.connect(self.add_record)
        self.editBtn.clicked.connect(self.edit_record)
        self.deleteBtn.clicked.connect(self.delete_record)
        self.copyBtn.clicked.connect(self.copy_records)

    def set_month_and_year(self):
        """
        Sets initial values for year and month boxes.
        """
        self.yearBox.addItems(YEARS)
        self.monthBox.addItems(MONTHS)
        current_date = QDate.currentDate()
        self.yearBox.setCurrentText(str(current_date.year()))
        self.monthBox.setCurrentText(MONTHS[current_date.month()])

    def setup_table(self):
        """
        Initializes the table for budget records.
        """
        self.records = TableModel(("Amount", "Category", "Type", "On day"))  # FIXME to enums
        self.recordsView.setModel(self.records)
        self.selection = QItemSelectionModel(self.records)
        self.recordsView.setSelectionModel(self.selection)

    def load_budget_records(self):
        """
        Loads the data from DB to GUI.
        """
        self.records.prepare()
        month = self.monthBox.currentIndex()  # by position
        year = self.yearBox.currentText()
        records = self.orm.fetch_records(month, year)
        for r in records:
            self.records.addRow(r)

    def add_record(self):
        """
        Fires up GUI for budget record creation.
        """
        if len(self.categories) == 0:
            show_warning('You have to create categories first.')
            return

        manager = Manager(self.categories.values())
        manager.createdRecord.connect(self.record_created)
        manager.exec()

    def edit_record(self):
        """
        Fires up GUI for budget record editing.
        """
        index = self.selection.currentIndex()
        if index.isValid():
            record = index.data(role=Qt.UserRole)
            manager = Manager(self.categories.values(), record)
            manager.editedRecord.connect(self.record_edited)
            manager.exec()

    def delete_record(self):
        """
        Deletes the budget record from DB and GUI.
        """
        index = self.selection.currentIndex()
        if index.isValid():
            record = index.data(role=Qt.UserRole)
            self.orm.delete_record(record)
            self.records.removeRows(index.row(), 1)

    def copy_records(self):
        pass  # TODO __FUTURE__

    def record_created(self, amount, category_id, budget_type, day, year,
                       month):
        """
        Adds created budget record into DB and GUI.
        """
        record = self.orm.add_record(amount, category_id, budget_type, day,
                                         year, month)
        self.records.addRow(record)

    def record_edited(self, amount, category_id, budget_type, day, year,
                      month, record_id):
        """
        Adds edited budget record into DB and reloads all records in the GUI.
        """
        self.orm.update_record(amount, category_id, budget_type, day, year,
                               month, record_id)
        self.load_budget_records()
