from payment_engine.database.sqlite import db


class SQLiteReconciliationReportRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, merchant_id, record):
        cursor = self.db.cursor()

        cursor.execute("""
        INSERT INTO reconciliation_report_records (
            merchant_id,
            reference,
            amount,
            currency
        )
        VALUES (?, ?, ?, ?)
        """, (
            merchant_id,
            record.get("reference"),
            record.get("amount"),
            record.get("currency"),
        ))

        self.db.commit()

        return record

    def list(self, merchant_id):
        cursor = self.db.cursor()

        cursor.execute("""
        SELECT
            reference,
            amount,
            currency
        FROM reconciliation_report_records
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
            "DELETE FROM reconciliation_report_records"
        )

        self.db.commit()
