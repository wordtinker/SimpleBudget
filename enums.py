ACCOUNT_TYPES = ('Bank', 'Cash', 'Credit Card')


class Item:
    def __getitem__(self, item):
        return getattr(self, self._attrs[item])

    def __len__(self):
        return len(self._attrs)


class Account(Item):
    _attrs = ('name', 'type', 'balance', 'closed', 'exbudget', 'extotal', 'id')

    def __init__(self, name, acc_type, balance, closed, exbudget, extotal, acc_id):
        self.id = acc_id
        self.type = acc_type
        self.name = name
        self.balance = balance  # FIXME it's just a real number
        self.closed = closed
        self.exbudget = exbudget
        self.extotal = extotal


class Transaction(Item):
    _attrs = ('date', 'amount', 'info', 'account', 'category', 'id')

    def __init__(self, date, amount, info, acc_id , cat_id , trans_id):
        self.date = date
        self.amount = amount / 100    # from cents
        self.info = info
        self.account = acc_id
        self.category = cat_id
        self.id = trans_id
