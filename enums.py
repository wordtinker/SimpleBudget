ACCOUNT_TYPES = ('Bank', 'Cash', 'Credit Card')


class Account:
    _attrs = ('name', 'type', 'balance', 'closed', 'exbudget', 'extotal', 'id')

    def __init__(self, name, acc_type, balance, closed, exbudget, extotal, acc_id):
        self.id = acc_id
        self.type = acc_type
        self.name = name
        self.balance = balance  # FIXME it's just a real number
        self.closed = closed
        self.exbudget = exbudget
        self.extotal = extotal

    def __getitem__(self, item):
        return getattr(self, self._attrs[item])

    def __len__(self):
        return len(self._attrs)