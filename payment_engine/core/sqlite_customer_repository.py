"""
SQLite Customer Repository
"""

import sqlite3

from payment_engine.core.customer import Customer


class SQLiteCustomerRepository:

    def __init__(self, database="swift_payment_engine.db"):
        self.connection = sqlite3.connect(database)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                subscription TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def save(self, customer: Customer):
        self.connection.execute(
            """
            INSERT OR REPLACE INTO customers
            (email, name, subscription, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                customer.email,
                customer.name,
                customer.subscription,
                customer.status,
            ),
        )
        self.connection.commit()

    def get(self, email):

        row = self.connection.execute(
            """
            SELECT
                email,
                name,
                subscription,
                status
            FROM customers
            WHERE email=?
            """,
            (email,),
        ).fetchone()

        if row is None:
            return None

        return Customer(
            name=row[1],
            email=row[0],
            subscription=row[2],
            status=row[3],
        )

    def count(self):
        return self.connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]
