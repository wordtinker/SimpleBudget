from PyQt5.Qt import QDialog, pyqtSignal
import ui.selectMonth
from enums import YEARS, MONTHS


class Selector(ui.selectMonth.Ui_Dialog, QDialog):
    monthSelected = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.monthBox.addItems(MONTHS[1:])
        self.yearBox.addItems(YEARS)

    def accept(self):
        self.monthSelected.emit(self.monthBox.currentIndex() + 1,
                                int(self.yearBox.currentText()))
        QDialog.accept(self)
