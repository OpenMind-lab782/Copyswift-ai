import sqlite3
import atexit
from pathlib import Path

from payment_engine.database.migrations import MigrationManager

DEFAULT_DB_NAME = "swift_payment.db"


class SQLiteDatabase:

    def __init__(self, database_path=None):
        self.database_path = database_path or DEFAULT_DB_NAME
        self.database_path = str(Path(self.database_path))

        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.initialize()

    def initialize(self):

        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            reference TEXT PRIMARY KEY,
            merchant_id TEXT,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            gateway TEXT,
            customer_email TEXT,
            metadata TEXT,
            idempotency_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL,
            event TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT,
            metadata TEXT
        )
        """)

        self.connection.commit()

        MigrationManager(self).initialize()

    def begin(self):
        self.connection.execute("BEGIN")

    def cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


db = SQLiteDatabase()

atexit.register(db.close)
