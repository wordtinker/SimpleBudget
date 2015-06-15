""" Assorted utility functions. """
from collections import namedtuple
import decimal
import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange, monthcalendar
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


def _from_date_to_period(month, year):
    """
    Converts month and year into starting and ending date of period.
    Month 0 is considered full year.
    """
    if month == 0:
        f_day = datetime.date(year, 1, 1)
        l_day = datetime.date(year, 12, 31)
    else:
        _, lastday = monthrange(year, month)
        f_day = datetime.date(year, month, 1)
        l_day = datetime.date(year, month, lastday)

    return f_day, l_day


def _from_str_to_date(date):
    year, month, day = (int(i) for i in date.split('-'))
    return datetime.date(year, month, day)

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
    _attrs = ('name', 'balance', 'type', 'closed', 'exbudget', 'id')

    def __init__(self, name, acc_type, balance, closed, exbudget, acc_id):
        self.id = acc_id
        self.type = acc_type
        self.name = name
        self.balance = from_cents(balance)
        self.closed = closed
        self.exbudget = exbudget


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

    def fetch_budget_for_month(self, month, year, category):
        if month == 0:
            budget, *_ = self.storage.select_budget_for_year(year, category.id)
        else:
            budget, *_ = self.storage.select_budget(month, year, category.id)
        return from_cents(budget or 0)

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
        for category in subcategories.values():
            budget = self.fetch_budget_for_month(month, year, category)
            fact = self.fetch_summary_for_month(month, year, category)

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

    def fetch_budget_prediction(self, month, year, transaction_date):
        """
        Fetches predictions for a given period.

        """
        min_period, max_period = _from_date_to_period(month, year)

        min_period = min(transaction_date, min_period)

        m = min_period.month
        for y in range(min_period.year, max_period.year+1):
            while True:
                budget_records = self.fetch_records(m, y)
                for record in budget_records:
                    for prediction in self._predict(record, transaction_date):
                        if prediction:
                            yield prediction

                if (m, y) == (max_period.month, max_period.year) or m == 12:
                    m = 1
                    break
                else:
                    # Move to the next month
                    m += 1

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
        date = _from_str_to_date(date)
        return Transaction(date, amount, info, category_name,
                           rowid, category_id)

    def fetch_transactions_for_month(self, month, year, category):
        f_day, l_day = _from_date_to_period(month, year)

        results = self.storage.select_budget_transactions_for_category(
            f_day, l_day, category.id)
        transactions = [self._build_transaction(t) for t in results]

        return transactions

    def fetch_summary_for_month(self, month, year, category: Category):
        f_day, l_day = _from_date_to_period(month, year)

        total, *_ = self.storage.select_summary(f_day, l_day, category.id)
        return from_cents(total or 0)

    def fetch_transactions_for_period(self, month, year):
        f_day, l_day = _from_date_to_period(month, year)

        transactions = [self._build_transaction(t)
                        for t in self.storage.select_transactions_for_period(
                        f_day, l_day)]
        return transactions

    def fetch_transactions(self, account):
        transactions = [self._build_transaction(t)
                        for t in self.storage.select_transactions(account.id)]

        return transactions

    def fetch_balance_to_date(self, month, year):
        # Get the last transaction date
        last_transaction, *_ = self.storage.select_last_date()
        last_transaction = _from_str_to_date(last_transaction)
        last_transaction += relativedelta(days=1)
        # Get the first day of report period
        if month in (0, 1):
            last_day = datetime.date(year, 1, 1)
        else:
            last_day = datetime.date(year, month, 1)

        last_day = min(last_day, last_transaction)

        balance, *_ = self.storage.select_balance_till(last_day)
        return last_day, from_cents(balance or 0)

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

    # Predictors

    def _predict(self, record: Record, transaction_date):
        funcs = {
            'Monthly': self._monthly_predictor,
            'Point': self._point_predictor,
            'Daily': self._daily_predictor,
            'Weekly':  self._weekly_predictor
        }

        return funcs[record.type](record, transaction_date)

    def _monthly_predictor(self, record, transaction_date):
        category = self.fetch_subcategory(record.category_id)
        _, lastday = monthrange(record.year, record.month)
        last_day = datetime.date(record.year, record.month, lastday)
        budget = record.amount
        fact = self.fetch_summary_for_month(record.month, record.year, category)

        if budget == 0 or transaction_date >= last_day:
            yield None
        else:
            if budget > 0 and fact >= 0:  # Income
                expectation = max(budget - fact, 0)
            elif budget < 0 and fact <= 0:  # Spending
                expectation = min(budget - fact, 0)
            else:  # budget and fact have different signs, error
                # Stick to the plan
                expectation = budget
            yield Prediction(last_day, expectation, category)

    def _point_predictor(self, record, transaction_date):
        category = self.fetch_subcategory(record.category_id)
        budget_date = datetime.date(record.year, record.month, record.day)
        if transaction_date >= budget_date:
            # Budget record has expired
            yield None
        else:
            yield Prediction(budget_date, record.amount, category)

    def _daily_predictor(self, record, transaction_date):
        category = self.fetch_subcategory(record.category_id)
        _, last_day = monthrange(record.year, record.month)
        budget = record.amount / last_day
        for i in range(1, last_day+1):
            budget_date = datetime.date(record.year, record.month, i)
            if transaction_date >= budget_date:
                yield None
            else:
                yield Prediction(budget_date, budget, category)

    def _weekly_predictor(self, record, transaction_date):
        category = self.fetch_subcategory(record.category_id)
        day = record.day - 1  # Natural day of week order to array index
        # Calculate the dates of budget spending
        budget_days = [datetime.date(record.year, record.month, week[day])
                       for week in monthcalendar(record.year, record.month)
                       if week[day] != 0]
        budget = record.amount / len(budget_days)
        for day in budget_days:
            if transaction_date >= day:
                yield None
            else:
                yield Prediction(day, budget, category)
