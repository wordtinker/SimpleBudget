""" Assorted utility functions. """
from collections import namedtuple
import decimal
from PyQt5.Qt import QMessageBox
from storage import Storage


def show_warning(text):
    """
    Shows a simple warning with given text.
    """
    msg_box = QMessageBox()
    msg_box.setText(text)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    msg_box.exec()


def from_cents(cents: int):
    """
    Converts the int number of cents to decimal using proper math for
    currency.
    """
    return decimal.Decimal(str(cents)) / decimal.Decimal('100')


def to_cents(full: float):
    """
    Converts float currency into cents using proper math for currency.
    """
    return int(decimal.Decimal(str(full)) * decimal.Decimal('100'))


class Account:
    """
    Using separate class because we need to set attributes in the
    accountsManager, can't use namedtuple.
    """
    _attrs = ('name', 'balance', 'type', 'closed', 'exbudget', 'extotal', 'id')

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
    """
    Builds Transaction object given query result and categories dictionary.
    """
    date, amount, info, category_id, rowid = query_result
    name, parent, _ = categories[category_id]
    category = parent + '::' + name
    amount = from_cents(amount)
    return Transaction(date, amount, info, category, rowid, category_id)

Record = namedtuple('Record', ['amount', 'category', 'type', 'day',
                               'year', 'month', 'id', 'category_id'])


def build_record(query_result, categories):
    """
    Builds Record object given query result and categories dictionary.
    """
    amount, category_id, budget_type, day, year, month, rowid = query_result
    name, parent, _ = categories[category_id]
    category = parent + '::' + name
    amount = from_cents(amount)
    return Record(amount, category, budget_type, day, year, month,
                  rowid, category_id)

Category = namedtuple('Category', ['name', 'parent', 'id'])

BudgetBar =\
    namedtuple('BudgetBar', ['category', 'value', 'maximum', 'expectation'])


class ORM:
    def __init__(self, file_name):
        self.storage = Storage(file_name)

    # Accounts #

    def fetch_accounts_summary(self):
        accounts = [Account(*a) for a in self.storage.select_accounts_summary()]
        return accounts

    def fetch_accounts(self):
        accounts = [Account(*a) for a in self.storage.select_accounts()]
        return accounts

    def update_account_type(self, account, text):
        self.storage.update_account_type(account.id, text)

    def update_account_status(self, account, state):
        self.storage.update_account_status(account.id, state)

    def update_account_budget_status(self, account, state):
        self.storage.update_account_budget_status(account.id, state)

    def update_account_total_status(self, account, state):
        self.storage.update_account_total_status(account.id, state)

    def add_account(self, name):
        acc = self.storage.add_account(name)
        return Account(*acc)

    def delete_account(self, account):
        return self.storage.delete_account(account.id)

    # Budget records #

    def fetch_records(self, month, year):
        categories = self.fetch_subcategories()
        records = [build_record(r, categories)
                   for r in self.storage.select_records(month, year)]
        return records

    def delete_record(self, record):
        self.storage.delete_record(record.id)

    def add_record(self, amount, category_id, budget_type, day,
                                         year, month):  # FIXME cat_id
        result = self.storage.add_record(amount, category_id, budget_type, day,
                                         year, month)
        categories = self.fetch_subcategories()
        record = build_record(result, categories)
        return record

    def update_record(self, amount, category_id, budget_type, day, year,
                                   month, record_id):
        self.storage.update_record(amount, category_id, budget_type, day, year,
                                   month, record_id)

    def fetch_budget_report_bars(self, month, year):  # TODO ORM + review
        """
        Fetches from DB budgets and transactions for each category and turns them
        into BuadgetBar.
        """
        categories = self.fetch_subcategories()

        for record in self.storage.get_budget_report(month, year):
            category_id, budget, fact = record
            budget = from_cents(budget or 0)
            fact = from_cents(fact or 0)
            category = categories[category_id]

            if budget == 0 and fact == 0:
                continue
            elif budget >= 0 and fact >= 0:  # Income
                expectation = str(max(budget - fact, 0))
            elif budget <= 0 and fact <= 0:  # Spending
                expectation = str(min(budget - fact, 0))
                budget = -budget
                fact = -fact
            else:  # budget and fact have different signs, error
                expectation = 'Error'
                budget = abs(budget)
                fact = abs(fact)

            yield BudgetBar(category, fact, budget, expectation)  # FIXME

    # Categories #

    def fetch_parents(self):
        parents = self.storage.select_parents()
        return [Category(*p) for p in parents]

    def fetch_subcategories_for_parent(self, category):
        subs = self.storage.select_subcategories(category.name)
        subs = [Category(*c) for c in subs]
        return subs

    def fetch_subcategories(self, full=True):
        """
        Builds dictionary of subcategories.
        :return: dic
        """
        subs = self.storage.select_all_subcategories()
        categories = dict(((rowid, Category(name, parent, rowid))
                          for name, parent, rowid in subs))

        # Add empty category
        if full:
            categories[0] = Category(' - - - ', '', 0)

        return categories

    def delete_category(self, category):
        if category.parent is not None:
            return self.storage.delete_subcategory(category.id)
        else:
            return self.storage.delete_category(category.name)

    def add_category(self, name, parent):
        if parent == '':
            return self.storage.add_category(name)
        else:
            return self.storage.add_subcategory(name, parent)

    # Transactions #

    def fetch_transactions_for_month(self, month, year, category):
        categories = self.fetch_subcategories()  # TODO transit to self.categories
        results = self.storage.select_transactions_for_month(
            month, year, category.id)
        transactions = [build_transaction(t, categories)
                        for t in results]

        return transactions

    def fetch_transactions(self, account):
        categories = self.fetch_subcategories()
        transactions = [build_transaction(t, categories)
                        for t in self.storage.select_transactions(account.id)]

        return transactions

    def delete_transaction(self, transaction, account):
        self.storage.delete_transaction(transaction.id, account.id)

    def add_transaction(self, date, amount, info, account, category_id):  # FIXME cat ID
        categories = self.fetch_subcategories()
        tr = self.storage.add_transaction(date, amount, info, account.id, category_id)
        transaction = build_transaction(tr, categories)
        return transaction

    def update_transaction(self, trans_id, account, date, amount, info, category_id): # FIXME cat ID
        self.storage.update_transaction(
            trans_id, account.id, date, amount, info, category_id)
