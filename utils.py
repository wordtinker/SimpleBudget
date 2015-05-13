from collections import namedtuple
import decimal


def from_cents(cents: int):
    return decimal.Decimal(str(cents)) / decimal.Decimal('100')


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
