"""
Payment History Repository
"""

import sqlite3


class PaymentHistoryRepository:

    def __init__(self, database="swift_payment_engine.db"):
        self.connection = sqlite3.connect(database)

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE,
                customer_email TEXT,
                gateway TEXT,
                amount REAL,
                currency TEXT,
                status TEXT
            )
            """
        )

        self.connection.commit()

    def exists(self, reference):

        row = self.connection.execute(
            """
            SELECT 1
            FROM payment_history
            WHERE reference=?
            """,
            (reference,),
        ).fetchone()

        return row is not None

    def save(
        self,
        reference,
        customer_email,
        gateway,
        amount,
        currency,
        status,
    ):

        if self.exists(reference):
            return False

        self.connection.execute(
            """
            INSERT INTO payment_history
            (
                reference,
                customer_email,
                gateway,
                amount,
                currency,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                reference,
                customer_email,
                gateway,
                amount,
                currency,
                status,
            ),
        )

        self.connection.commit()

        return True

    def all(self):

        cursor = self.connection.execute(
            """
            SELECT
                reference,
                customer_email,
                gateway,
                amount,
                currency,
                status
            FROM payment_history
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()
