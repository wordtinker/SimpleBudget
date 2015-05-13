from collections import namedtuple

ACCOUNT_TYPES = ('Bank', 'Cash', 'Credit Card')
YEARS = ('2014', '2015', '2016', '2017', '2018')
MONTHS = ('All', 'Jan', 'Feb', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December')
BUDGET_TYPES = ('Monthly', 'Point', 'Daily', 'Weekly')






Category = namedtuple('Category', ['name', 'parent', 'id'])

Record = namedtuple('Record', ['amount', 'category', 'type', 'day',
                               'year', 'month', 'id', 'category_id'])