import sqlite3
import datetime
from calendar import monthrange

from enums import ACCOUNT_TYPES


class Storage:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db_conn = sqlite3.connect(db_path)

        # Initialize tables
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Accounts(
        name TEXT,
        type TEXT,
        balance INTEGER,
        closed INTEGER,
        exbudget INTEGER,
        extotal INTEGER)""")
        self.db_conn.commit()

        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions(
        date DATE,
        amount INTEGER,
        info TEXT,
        acc_id INTEGER,
        category_id INTEGER)""")
        self.db_conn.commit()

        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories(
        name TEXT UNIQUE)""")
        self.db_conn.commit()

        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subcategories(
        name TEXT,
        parent TEXT,
        UNIQUE(name, parent))""")
        self.db_conn.commit()

        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS Budget(
        amount INTEGER,
        category_id INTEGER,
        type TEXT,
        day INTEGER,
        year INTEGER,
        month INTEGER
        )""")
        self.db_conn.commit()

    # #################### Accounts ########################

    def select_accounts_summary(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT *, rowid
        FROM Accounts
        WHERE closed = 0""")
        return db_cursor.fetchall()

    def select_accounts(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT *, rowid
        FROM Accounts""")
        return db_cursor.fetchall()

    def update_account_type(self, acc_id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET type=?
        WHERE rowid=?
        """, (value, acc_id))
        self.db_conn.commit()

    def update_account_status(self, acc_id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET closed=?
        WHERE rowid=?
        """, (value, acc_id))
        self.db_conn.commit()

    def update_account_budget_status(self, acc_id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET exbudget=?
        WHERE rowid=?
        """, (value, acc_id))
        self.db_conn.commit()

    def update_account_total_status(self, acc_id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET extotal=?
        WHERE rowid=?
        """, (value, acc_id))
        self.db_conn.commit()

    def add_account(self, acc_name):
        acc = (acc_name, ACCOUNT_TYPES[0], 0, 0, 0, 0)
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        INSERT INTO Accounts
        VALUES(?, ?, ?, ?, ?, ?)
        """, acc)
        self.db_conn.commit()
        rowid = db_cursor.lastrowid
        return acc + (rowid, )

    def delete_account(self, acc_id):
        # Cant delete if there is a transaction on account
        if self.exists_transaction(acc_id):
            return False

        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Accounts
        WHERE rowid=?
        """, (acc_id, ))
        self.db_conn.commit()
        return True

    def update_total(self, acc_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT SUM(amount)
        FROM Transactions
        WHERE acc_id=?
        """, (acc_id, ))
        total, *_ = db_cursor.fetchone()
        if total is None:
            total = 0

        db_cursor.execute("""
        UPDATE Accounts
        SET balance=?
        WHERE rowid=?
        """, (total, acc_id))
        self.db_conn.commit()

    # ################### Transactions #####################

    def select_transactions(self, acc_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT date, amount, info, category_id, rowid
        FROM Transactions
        WHERE acc_id = ?
        ORDER BY date ASC""", (acc_id,))
        return db_cursor.fetchall()

    def exists_transaction(self, acc_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT COUNT(*)
        FROM Transactions
        WHERE acc_id = ?""", (acc_id,))
        count = db_cursor.fetchone()[0]
        return count > 0

    def select_summary(self, month, year, category_id):
        _, lastday = monthrange(year, month)
        f_day = datetime.date(year, month, 1)
        l_day = datetime.date(year, month, lastday)
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT sum(t.amount) FROM Transactions as t
        INNER JOIN Accounts as a
        on t.acc_id = a.rowid
        WHERE date BETWEEN ? AND ?
        AND category_id=?
        AND exbudget = 0""", (f_day, l_day, category_id))
        return db_cursor.fetchone()

    def select_transactions_for_category(self, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT *, rowid
        FROM Transactions
        WHERE category_id = ?""", (category_id,))
        return db_cursor.fetchall()

    def exists_transaction_for_category(self, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT COUNT(*)
        FROM Transactions
        WHERE category_id = ?""", (category_id,))
        count = db_cursor.fetchone()[0]
        return count > 0

    def add_transaction(self, date, amount, info, acc_id, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        INSERT INTO Transactions
        VALUES(?, ?, ?, ?, ?)
        """, (date, amount, info, acc_id, category_id))
        self.db_conn.commit()
        rowid = db_cursor.lastrowid
        self.update_total(acc_id)
        return date.isoformat(), amount, info, category_id, rowid

    def update_transaction(self, trans_id, acc_id,  date, amount, info,
                           category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Transactions
        SET date=?, amount=?, info=?, category_id=?
        WHERE rowid=?
        """, (date, amount, info, category_id, trans_id))
        self.db_conn.commit()
        self.update_total(acc_id)

    def delete_transaction(self, trans_id, acc_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Transactions
        WHERE rowid=?
        """, (trans_id, ))
        self.db_conn.commit()
        self.update_total(acc_id)

    # #################### Categories #####################

    def select_parents(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT name, NULL, rowid
        FROM Categories
        ORDER BY name ASC""", ())
        return db_cursor.fetchall()

    def select_subcategories(self, category):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT name, parent, rowid
        FROM Subcategories
        WHERE parent=?""", (category, ))
        return db_cursor.fetchall()

    def exists_subcategory(self, category):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT COUNT(*)
        FROM Subcategories
        WHERE parent=?""", (category, ))
        count = db_cursor.fetchone()[0]
        return count > 0

    def select_all_subcategories(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT name, parent, rowid
        FROM Subcategories
        ORDER BY parent, name""", ())
        return db_cursor.fetchall()

    def add_category(self, name):
        db_cursor = self.db_conn.cursor()
        try:
            db_cursor.execute("""
            INSERT INTO Categories
            VALUES(?)
            """, (name,))
            self.db_conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_subcategory(self, name, parent):
        db_cursor = self.db_conn.cursor()
        try:
            db_cursor.execute("""
            INSERT INTO Subcategories
            VALUES(?, ?)
            """, (name, parent))
            self.db_conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_category(self, category):
        # Can't delete if there is a child category
        if self.exists_subcategory(category):
            return False

        # Delete the category
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Categories
        WHERE name=?
        """, (category, ))
        self.db_conn.commit()
        return True

    def delete_subcategory(self, category_id):
        # Can't delete if there is a transaction or budget record
        if (self.exists_transaction_for_category(category_id) or
                self.exists_record_for_category(category_id)):
            return False

        # Delete the subcategory
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Subcategories
        WHERE rowid=?
        """, (category_id, ))
        self.db_conn.commit()
        return True

# #################### Budgets ########################

    def select_records(self, month, year):
        db_cursor = self.db_conn.cursor()
        if month == 0:
            db_cursor.execute("""
            SELECT *, rowid
            FROM Budget
            WHERE year=?""", (year,))
        else:
            db_cursor.execute("""
            SELECT *, rowid
            FROM Budget
            WHERE month=? AND year=?""", (month, year))
        return db_cursor.fetchall()

    def select_budget(self, month, year, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT sum(amount) FROM Budget
        WHERE month=? AND year=? AND category_id=?""",
                          (month, year, category_id))
        return db_cursor.fetchone()

    def exists_record_for_category(self, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT COUNT(*)
        FROM Budget
        WHERE category_id = ?""", (category_id,))
        count = db_cursor.fetchone()[0]
        return count > 0

    def add_record(self, amount, category_id, budget_type, day, year, month):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        INSERT INTO Budget
        VALUES(?, ?, ?, ?, ?, ?)
        """, (amount, category_id, budget_type, day, year, month))
        self.db_conn.commit()
        rowid = db_cursor.lastrowid
        return amount, category_id, budget_type, day, year, month, rowid

    def update_record(self, amount, category_id, budget_type, day, year, month,
                      record_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Budget
        SET amount=?, category_id=?, type=?, day=?, year=?, month=?
        WHERE rowid=?
        """, (amount, category_id, budget_type, day, year, month, record_id))
        self.db_conn.commit()

    def delete_record(self, rowid):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Budget
        WHERE rowid=?
        """, (rowid, ))
        self.db_conn.commit()

    def get_budget_report(self, month, year):
        subcategories =\
            [cat_id for *_, cat_id in self.select_all_subcategories()]
        subcategories.append(0)  # Include no category id

        for cat_id in subcategories:
            budget, *_ = self.select_budget(month, year, cat_id)
            fact, *_ = self.select_summary(month, year, cat_id)
            yield (cat_id, budget, fact)
