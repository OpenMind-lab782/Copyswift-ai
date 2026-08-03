class MigrationManager:

    CURRENT_VERSION = 5

    def __init__(self, database):
        self.db = database

    def initialize(self):
        cursor = self.db.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        )
        """)

        cursor.execute("SELECT version FROM schema_version")

        row = cursor.fetchone()

        if row is None:
            cursor.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (self.CURRENT_VERSION,)
            )

        version = self.current_version()

        if version < 2:
            try:
                cursor.execute(
                    "ALTER TABLE payments ADD COLUMN idempotency_key TEXT"
                )
            except Exception:
                pass

            cursor.execute(
                "UPDATE schema_version SET version = ?",
                (2,)
            )


        if version < 3:
            try:
                cursor.execute(
                    "ALTER TABLE payment_events ADD COLUMN metadata TEXT"
                )
            except Exception:
                pass

            cursor.execute(
                "UPDATE schema_version SET version = ?",
                (3,)
            )


        if version < 4:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS settlements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_id TEXT NOT NULL,
                reference TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL
            )
            """)

            cursor.execute(
                "UPDATE schema_version SET version = ?",
                (4,)
            )



        if version < 5:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reconciliation_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_id TEXT NOT NULL,
                reference TEXT NOT NULL
            )
            """)

            cursor.execute(
                "UPDATE schema_version SET version = ?",
                (5,)
            )

        self.db.commit()


    def current_version(self):
        cursor = self.db.cursor()

        cursor.execute("SELECT version FROM schema_version")

        row = cursor.fetchone()

        if row is None:
            return 0

        if isinstance(row, dict):
            return row["version"]

        return row[0]
