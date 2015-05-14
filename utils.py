from collections import namedtuple
import decimal
from PyQt5.Qt import QMessageBox


def show_warning(text):
    msg_box = QMessageBox()
    msg_box.setText(text)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    msg_box.exec()


def from_cents(cents: int):
    return decimal.Decimal(str(cents)) / decimal.Decimal('100')


def to_cents(full: float):
    return int(decimal.Decimal(str(full)) * decimal.Decimal('100'))


class Account:
    """
    Using separate class because we need to set attributes in the
    accountsManager, can't use namedtuple.
    """
    _attrs = ('name', 'type', 'balance', 'closed', 'exbudget', 'extotal', 'id')

    def __init__(self, name, acc_type, balance, closed, exbudget, extotal,
                 acc_id):
        self.id = acc_id
        self.type = acc_type
        self.name = name
        self.balance = from_cents(balance)
        self.closed = closed
        self.exbudget = exbudget
        self.extotal = extotal

    def __getitem__(self, item):
        return getattr(self, self._attrs[item])

    def __len__(self):
        return len(self._attrs)

Transaction = namedtuple(
    'Transaction', ['date', 'amount', 'info', 'category', 'id', 'category_id'])


def build_transaction(query_result, categories):
    date, amount, info, category_id, rowid = query_result
    name, parent, _ = categories[category_id]
    category = parent + '::' + name
    amount = from_cents(amount)
    return Transaction(date, amount, info, category, rowid, category_id)

Record = namedtuple('Record', ['amount', 'category', 'type', 'day',
                               'year', 'month', 'id', 'category_id'])


def build_record(query_result, categories):
    amount, category_id, budget_type, day, year, month, rowid = query_result
    name, parent, _ = categories[category_id]
    category = parent + '::' + name
    amount = from_cents(amount)
    return Record(amount, category, budget_type, day, year, month,
                  rowid, category_id)

Category = namedtuple('Category', ['name', 'parent', 'id'])
