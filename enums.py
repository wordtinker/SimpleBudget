from collections import namedtuple

ACCOUNT_TYPES = ('Bank', 'Cash', 'Credit Card')


class Account:
    """
    Using separate class because we need to set attributes, can't use tuple.
    """
    _attrs = ('name', 'type', 'balance', 'closed', 'exbudget', 'extotal', 'id')

    def __init__(self, name, acc_type, balance, closed, exbudget, extotal, acc_id):
        self.id = acc_id
        self.type = acc_type
        self.name = name
        self.balance = balance
        self.closed = closed
        self.exbudget = exbudget
        self.extotal = extotal

    def __getitem__(self, item):
        return getattr(self, self._attrs[item])

    def __len__(self):
        return len(self._attrs)

Transaction = namedtuple('Transaction', ['date', 'amount', 'info', 'category', 'category_id', 'id'])

Category = namedtuple('Category', ['name', 'parent', 'id'])