from PyQt5.QtWidgets import QDialog, QHeaderView
from PyQt5.Qt import QDate, QItemSelectionModel, Qt

from calendar import monthrange
import ui.manageBudget
from recordManager import Manager
from monthSelector import Selector
from models import TableModel
from enums import YEARS, MONTHS
from utils import show_warning, to_cents

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

        self.recordsView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

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
        self.monthBox.addItems(MONTHS[1:])
        current_date = QDate.currentDate()
        self.yearBox.setCurrentText(str(current_date.year()))
        self.monthBox.setCurrentText(MONTHS[current_date.month()])

    def setup_table(self):
        """
        Initializes the table for budget records.
        """
        self.records = TableModel(("Amount", "Category", "Type", "On day"))
        self.recordsView.setModel(self.records)
        self.selection = QItemSelectionModel(self.records)
        self.recordsView.setSelectionModel(self.selection)

    def load_budget_records(self):
        """
        Loads the data from DB to GUI.
        """
        self.records.prepare()
        month = self.monthBox.currentIndex() + 1  # by position+1
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
        dialog = Selector()
        dialog.monthSelected.connect(self.copy_from_month)
        dialog.exec()

    def copy_from_month(self, month, year):
        records = self.orm.fetch_records(month, year)
        new_month = self.monthBox.currentIndex() + 1
        new_year = int(self.yearBox.currentText())
        _, last_day = monthrange(new_year, new_month)
        for rec in records:
            category = self.orm.fetch_subcategory(rec.category_id)
            amount = to_cents(rec.amount)
            new_day = min(last_day, rec.day)
            self.record_created(amount, category, rec.type, new_day,
                                new_year, new_month)

    def record_created(self, amount, category, budget_type, day, year,
                       month):
        """
        Adds created budget record into DB and GUI.
        """
        record = self.orm.add_record(amount, category, budget_type, day,
                                     year, month)
        if (self.monthBox.currentIndex() + 1 == month and
                int(self.yearBox.currentText()) == year):
            self.records.addRow(record)

    def record_edited(self, amount, category, budget_type, day, year,
                      month, record_id):
        """
        Adds edited budget record into DB and reloads all records in the GUI.
        """
        self.orm.update_record(amount, category, budget_type, day, year,
                               month, record_id)
        self.load_budget_records()
