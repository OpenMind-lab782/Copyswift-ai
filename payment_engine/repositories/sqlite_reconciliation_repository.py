from payment_engine.database.sqlite import db


class SQLiteReconciliationRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, merchant_id, record):
        cursor = self.db.cursor()

        cursor.execute("""
        INSERT INTO reconciliation_records (
            merchant_id,
            reference
        )
        VALUES (?, ?)
        """, (
            merchant_id,
            record.get("reference"),
        ))

        self.db.commit()

        return record

    def list(self, merchant_id):
        cursor = self.db.cursor()

        cursor.execute("""
        SELECT
            merchant_id,
            reference
        FROM reconciliation_records
        WHERE merchant_id = ?
        ORDER BY id ASC
        """, (merchant_id,))

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def clear(self):
        cursor = self.db.cursor()

        cursor.execute(
            "DELETE FROM reconciliation_records"
        )

        self.db.commit()
