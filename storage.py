import sqlite3

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
        balance REAL,
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

    def update_account_type(self, id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET type=?
        WHERE rowid=?
        """, (value, id))
        self.db_conn.commit()

    def update_account_status(self, id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET closed=?
        WHERE rowid=?
        """, (value, id))
        self.db_conn.commit()

    def update_account_budget_status(self, id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET exbudget=?
        WHERE rowid=?
        """, (value, id))
        self.db_conn.commit()

    def update_account_total_status(self, id, value):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Accounts
        SET extotal=?
        WHERE rowid=?
        """, (value, id))
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

    def delete_account(self, acc_id):  # TODO Cascade delete transactions or forbid deletion?
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Accounts
        WHERE rowid=?
        """, (acc_id, ))
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

    def select_transactions_for_category(self, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT *, rowid
        FROM Transactions
        WHERE category_id = ?""", (category_id,))
        return db_cursor.fetchall()

    def add_transaction(self, date, amount, info, acc_id, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        INSERT INTO Transactions
        VALUES(?, ?, ?, ?, ?)
        """, (date, amount, info, acc_id, category_id))
        self.db_conn.commit()
        rowid = db_cursor.lastrowid
        return date.isoformat(), amount, info, category_id, rowid

    def update_transaction(self, trans_id, date, amount, info, category_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        UPDATE Transactions
        SET date=?, amount=?, info=?, category_id=?
        WHERE rowid=?
        """, (date, amount, info, category_id, trans_id))
        self.db_conn.commit()

    def delete_transaction(self, trans_id):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Transactions
        WHERE rowid=?
        """, (trans_id, ))
        self.db_conn.commit()

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

    def select_all_subcategories(self):
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        SELECT name, parent, rowid
        FROM Subcategories""", ())
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
        children = self.select_subcategories(category)
        if len(children) > 0:
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
        # Can't delete if there is a transaction
        transactions = self.select_transactions_for_category(category_id)
        if len(transactions) > 0:
            return False

        # Delete the subcategory
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Subcategories
        WHERE rowid=?
        """, (category_id, ))
        self.db_conn.commit()
        return True