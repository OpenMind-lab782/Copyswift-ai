class MigrationManager:

    CURRENT_VERSION = 1

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
