""" Assorted utility functions. """
from collections import namedtuple
import decimal
import datetime
from calendar import monthrange
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

class ModelCore:
    """
    The core of QT model. Must implement [i] and len() interface.
    """
    def __getitem__(self, item):
        return getattr(self, self._attrs[item])

    def __len__(self):
        return len(self._attrs)


class Account(ModelCore):
    """
    Account model class. Attributes can be changed while editing.
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

class Transaction(ModelCore):
    """
    Transaction model class. Attributes can be changed while editing.
    """
    _attrs = ('date', 'amount', 'info', 'category', 'id', 'category_id')

    def __init__(self, date, amount, info, category, trans_id, category_id):
        self.date = date
        self.amount = amount
        self.info = info
        self.category = category
        self.id = trans_id
        self.category_id = category_id

Record = namedtuple('Record', ['amount', 'category', 'type', 'day',
                               'year', 'month', 'id', 'category_id'])

Category = namedtuple('Category', ['name', 'parent', 'id'])

BudgetBar =\
    namedtuple('BudgetBar', ['category', 'value', 'maximum', 'expectation'])
Prediction = namedtuple('Prediction', ['date', 'amount', 'category'])

class ORM:
    NO_CATEGORY = {
        'PARENT': '',
        'NAME': '- - -',
        'ID': 0
    }

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

    def _build_record(self, query_result):
        """
        Builds Record object given query result and categories dictionary.
        """
        amount, category_id, budget_type, day, year, month, rowid = query_result
        category = self.fetch_subcategory(category_id)
        category_name = category.parent + '::' + category.name
        amount = from_cents(amount)
        return Record(amount, category_name, budget_type, day, year, month,
                      rowid, category_id)

    def fetch_records(self, month, year):
        if month == 0:
            records = self.storage.select_records_for_year(year)
        else:
            records = self.storage.select_records(month, year)
        records = [self._build_record(r) for r in records]
        return records

    def delete_record(self, record):
        self.storage.delete_record(record.id)

    def add_record(self, amount, category, budget_type, day, year, month):
        result = self.storage.add_record(amount, category.id, budget_type,
                                         day, year, month)
        record = self._build_record(result)
        return record

    def update_record(self, amount, category, budget_type, day, year,
                                   month, record_id):
        self.storage.update_record(amount, category.id, budget_type, day, year,
                                   month, record_id)

    def fetch_budget_report_bars(self, month, year):
        """
        Fetches from DB budgets and transactions for each category and turns
        them into BudgetBar.
        """
        subcategories = self.fetch_subcategories()
        for category_id, category in subcategories.items():
            if month == 0:
                f_day = datetime.date(year, 1, 1)
                l_day = datetime.date(year, 12, 31)
                budget, *_ = self.storage.select_budget_for_year(
                    year, category_id)
            else:
                _, lastday = monthrange(year, month)
                f_day = datetime.date(year, month, 1)
                l_day = datetime.date(year, month, lastday)
                budget, *_ = self.storage.select_budget(
                    month, year, category_id)
            fact, *_ = self.storage.select_summary(f_day, l_day, category_id)

            budget = from_cents(budget or 0)
            fact = from_cents(fact or 0)

            if budget == 0 and fact == 0:
                continue
            elif budget >= 0 and fact >= 0:  # Income
                expectation = max(budget - fact, 0)
            elif budget <= 0 and fact <= 0:  # Spending
                expectation = min(budget - fact, 0)
                budget = -budget
                fact = -fact
            else:  # budget and fact have different signs, error
                expectation = 'Error'
                budget = abs(budget)
                fact = abs(fact)

            yield BudgetBar(category, fact, budget, str(expectation))

    def fetch_budget_prediction(self, month, year, today):
        # TODO budget type!!!
        # This part assumes budget type Monthly
        if month == 0:
            for new_month in range(1, 13):
                pass  # TODO depends on today
        else:
            _, lastday = monthrange(year, month)
            last_day = datetime.date(year, month, lastday)
            for record in self.storage.get_budget_report(month, year):
                category_id, budget, fact = record
                budget = from_cents(budget or 0)
                fact = from_cents(fact or 0)
                category = self.fetch_subcategory(category_id)

                if budget == 0:
                    continue
                elif budget > 0 and fact >= 0:  # Income
                    expectation = max(budget - fact, 0)
                elif budget < 0 and fact <= 0:  # Spending
                    expectation = min(budget - fact, 0)
                else:  # budget and fact have different signs, error
                    # Stick to the plan
                    expectation = budget

                yield Prediction(str(last_day), expectation, category)

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
            categories[self.NO_CATEGORY['ID']] =\
                Category(self.NO_CATEGORY['NAME'],
                         self.NO_CATEGORY['PARENT'],
                         self.NO_CATEGORY['ID'])

        return categories

    def fetch_subcategory(self, category_id):
        if category_id == self.NO_CATEGORY['ID']:
            return Category(self.NO_CATEGORY['NAME'],
                            self.NO_CATEGORY['PARENT'],
                            self.NO_CATEGORY['ID'])
        else:
            name, parent = self.storage.select_subcategory(category_id)
            return Category(name, parent, category_id)

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

    def _build_transaction(self, query_result):
        """
        Builds Transaction object given query result and categories dictionary.
        """
        date, amount, info, category_id, rowid = query_result
        category = self.fetch_subcategory(category_id)
        category_name = category.parent + '::' + category.name
        amount = from_cents(amount)
        return Transaction(date, amount, info, category_name, rowid, category_id)

    def fetch_transactions_for_month(self, month, year, category):
        if month == 0:
            f_day = datetime.date(year, 1, 1)
            l_day = datetime.date(year, 12, 31)
        else:
            _, lastday = monthrange(year, month)
            f_day = datetime.date(year, month, 1)
            l_day = datetime.date(year, month, lastday)

        results = self.storage.select_budget_transactions_for_category(
            f_day, l_day, category.id)
        transactions = [self._build_transaction(t) for t in results]

        return transactions

    def fetch_transactions_for_period(self, month, year):
        if month == 0:
            first_day = datetime.date(year, 1, 1)
            last_day = datetime.date(year, 12, 31)
        else:
            _, lastday = monthrange(year, month)
            first_day = datetime.date(year, month, 1)
            last_day = datetime.date(year, month, lastday)

        transactions = [self._build_transaction(t)
                        for t in self.storage.select_transactions_for_period(
                        first_day, last_day)]
        return transactions

    def fetch_transactions(self, account):
        transactions = [self._build_transaction(t)
                        for t in self.storage.select_transactions(account.id)]

        return transactions

    def fetch_balance_to_date(self, month, year):
        if month in (0, 1):
            last_day = datetime.date(year-1, 12, 31)
        else:
            month -= 1
            _, lastday = monthrange(year, month)
            last_day = datetime.date(year, month, lastday)

        balance, *_ = self.storage.select_balance_till(last_day)
        return str(last_day), from_cents(balance or 0)

    def delete_transaction(self, transaction, account):
        self.storage.delete_transaction(transaction.id, account.id)

    def add_transaction(self, date, amount, info, account, category):
        tr = self.storage.add_transaction(
            date, amount, info, account.id, category.id)
        transaction = self._build_transaction(tr)
        return transaction

    def update_transaction(self, transaction, account, category):
        self.storage.update_transaction(
            transaction.id, account.id, transaction.date, transaction.amount,
            transaction.info, category.id)
