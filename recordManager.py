from PyQt5.Qt import QDialog, pyqtSignal, QDate, Qt
from ui.manageRecord import Ui_Dialog
from calendar import monthrange
from models import CategoryListModel
from enums import YEARS, MONTHS, DAYS, BUDGET_TYPES
from utils import to_cents


class Manager(Ui_Dialog, QDialog):
    """
    GUI to handle creation and editing of budget record.
    """

    # amount, category_id, type, day, year, month
    createdRecord = pyqtSignal(int, object, str, int, int, int)
    # amount, category_id, type, day, year, month, record_id
    editedRecord = pyqtSignal(int, object, str, int, int, int, int)

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
            self.yearBox.setCurrentText(str(self.record.year))
            self.monthBox.setCurrentIndex(self.record.month - 1)
            self.dayBox.setCurrentText(str(self.record.day))
        else:
            today = QDate.currentDate()
            self.yearBox.setCurrentText(str(today.year()))
            self.monthBox.setCurrentIndex(today.month() - 1)

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
        self.monthBox.addItems(MONTHS[1:])

        # Set behaviour for days spinbox
        self.typeBox.currentTextChanged.connect(self.set_day_limit)
        self.yearBox.currentTextChanged.connect(self.set_day_limit)
        self.monthBox.currentTextChanged.connect(self.set_day_limit)

        self.typeBox.addItems(BUDGET_TYPES)

    def set_day_limit(self, _):
        """
        Changes allowed day limit depending on choosen budget type.
        """
        self.dayBox.clear()
        budget_type = self.typeBox.currentText()
        if budget_type in ('Monthly', 'Daily'):
            self.dayBox.setEnabled(False)
        elif budget_type == 'Point':
            year = int(self.yearBox.currentText())
            month = self.monthBox.currentIndex() + 1
            _, last_day = monthrange(year, month)
            self.dayBox.addItems(str(i) for i in range(1, last_day+1))
            self.dayBox.setEnabled(True)
        else:  # Weekly
            self.dayBox.addItems(DAYS)
            self.dayBox.setEnabled(True)

    def accept(self):
        """
        Gathers budget record params and sends signal.
        """
        amount = to_cents(self.budgetBox.value())
        category = self.categoryBox.currentData(role=Qt.UserRole)
        account_type = self.typeBox.currentText()
        on_day = self.dayBox.currentIndex() + 1
        year = int(self.yearBox.currentText())
        month = self.monthBox.currentIndex() + 1
        if self.record is None:
            self.createdRecord.emit(amount, category, account_type, on_day,
                                    year, month)
        else:
            self.editedRecord.emit(amount, category, account_type, on_day,
                                   year, month, self.record.id)
        QDialog.accept(self)
