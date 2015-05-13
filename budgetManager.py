from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import QDate, QItemSelectionModel, Qt

import ui.manageBudget
from recordManager import Manager
from models import TableModel
from enums import YEARS, MONTHS, Category, Record


class BudgetManager(ui.manageBudget.Ui_Dialog, QDialog):
    def build_record(self, DB_query_result):
        params = list(DB_query_result)

        category_id = params[1]
        name, parent, _ = self.categories[category_id]
        params[1] = parent + '::' + name
        params.append(category_id)

        params[0] /= 100  # From cents

        return Record(*params)

    def __init__(self, storage):
        super().__init__()
        self.setupUi(self)

        self.storage = storage

        # Fetch subcategories list
        subs = self.storage.select_all_subcategories()
        self.categories = dict(((rowid, Category(name, parent, rowid))
                                for name, parent, rowid in subs))

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
        self.yearBox.addItems(YEARS)
        self.monthBox.addItems(MONTHS)
        current_date = QDate.currentDate()
        self.yearBox.setCurrentText(str(current_date.year()))
        self.monthBox.setCurrentText(MONTHS[current_date.month()])

    def setup_table(self):
        self.records = TableModel(("Amount", "Category", "Type", "On day"))
        self.recordsView.setModel(self.records)
        self.selection = QItemSelectionModel(self.records)
        self.recordsView.setSelectionModel(self.selection)

    def load_budget_records(self):
        self.records.prepare()
        month = self.monthBox.currentIndex()  # by position
        year = self.yearBox.currentText()
        records = [self.build_record(r)
                   for r in self.storage.select_records(month, year)]
        for r in records:
            self.records.addRow(r)

    def add_record(self):
        manager = Manager(self.categories.values())
        manager.createdRecord.connect(self.record_created)
        manager.exec()

    def edit_record(self):
        index = self.selection.currentIndex()
        if index.isValid():
            record = index.data(role=Qt.UserRole)
            manager = Manager(self.categories.values(), record)
            manager.editedRecord.connect(self.record_edited)
            manager.exec()

    def delete_record(self):
        index = self.selection.currentIndex()
        if index.isValid():
            record = index.data(role=Qt.UserRole)
            self.storage.delete_record(record.id)
            self.records.removeRows(index.row(), 1)

    def copy_records(self):
        pass  # TODO __FUTURE__

    def record_created(self, amount, category_id, budget_type, day, year,
                       month):
        result = self.storage.add_record(amount, category_id, budget_type, day,
                                         year, month)
        record = self.build_record(result)
        self.records.addRow(record)

    def record_edited(self, amount, category_id, budget_type, day, year,
                       month, record_id):
        self.storage.update_record(amount, category_id, budget_type, day, year,
                       month, record_id)
        self.load_budget_records()
