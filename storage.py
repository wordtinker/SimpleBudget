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

    def delete_account(self, id):  # TODO Cascade delete transactions or forbid deletion?
        db_cursor = self.db_conn.cursor()
        db_cursor.execute("""
        DELETE FROM Accounts
        WHERE rowid=?
        """, (id, ))
        self.db_conn.commit()