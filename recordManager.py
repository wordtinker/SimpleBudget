from PyQt5.Qt import QDialog, pyqtSignal, QDate, Qt
from ui.manageRecord import Ui_Dialog
from models import CategoryListModel
from enums import YEARS, MONTHS, BUDGET_TYPES
from utils import to_cents


class Manager(Ui_Dialog, QDialog):
    """
    GUI to handle creation and editing of budget record.
    """

    # amount, category_id, type, day, year, month
    createdRecord = pyqtSignal(int, int, str, int, int, int)
    # amount, category_id, type, day, year, month, record_id
    editedRecord = pyqtSignal(int, int, str, int, int, int, int)

    def __init__(self, categories, record=None):
        super().__init__()
        self.setupUi(self)

        self.categories = categories
        self.record = record

        self.setup()

        if self.record:
            self.budgetBox.setValue(self.record.amount)
            self.categoryBox.setCurrentText(self.record.category)
            self.typeBox.setCurrentText(self.record.type)
            self.dayBox.setValue(self.record.day)
            self.yearBox.setCurrentText(str(self.record.year))
            self.monthBox.setCurrentIndex(self.record.month)
        else:
            today = QDate.currentDate()
            self.yearBox.setCurrentText(str(today.year()))
            self.monthBox.setCurrentIndex(today.month())

    def setup(self):
        """
        Initializes the GUI.
        """
        # List all categories
        self.categories_model = CategoryListModel()
        for cat in self.categories:
            self.categories_model.addItem(cat)
        self.categoryBox.setModel(self.categories_model)

        # Add years
        self.yearBox.addItems(YEARS)
        self.monthBox.addItems(MONTHS)

        # Set behaviour for days spinbox
        self.typeBox.currentTextChanged.connect(self.set_day_limit)

        self.typeBox.addItems(BUDGET_TYPES)

    def set_day_limit(self, budget_type):
        """
        Changes allowed day limit depending on choosen budget type.
        """
        if budget_type in ('Monthly', 'Daily'):
            self.dayBox.setMinimum(0)
            self.dayBox.setValue(0)
            self.dayBox.setEnabled(False)
        elif budget_type == 'Point':
            self.dayBox.setMinimum(1)
            self.dayBox.setMaximum(28)
            self.dayBox.setEnabled(True)
        else:  # Weekly
            self.dayBox.setMinimum(1)
            self.dayBox.setMaximum(7)
            self.dayBox.setEnabled(True)

    def accept(self):
        """
        Gathers budget record params and sends signal.
        """
        amount = to_cents(self.budgetBox.value())
        category_id = self.categoryBox.currentData(role=Qt.UserRole).id
        account_type = self.typeBox.currentText()
        on_day = self.dayBox.value()
        year = int(self.yearBox.currentText())
        month = self.monthBox.currentIndex()

        if self.record is None:
            self.createdRecord.emit(amount, category_id, account_type, on_day,
                                    year, month)
        else:
            self.editedRecord.emit(amount, category_id, account_type, on_day,
                                    year, month, self.record.id)
        QDialog.accept(self)
