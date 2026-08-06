from payment_engine.database.sqlite import db


class SQLiteSettlementRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, merchant_id, settlement):
        cursor = self.db.cursor()

        cursor.execute("""
        INSERT INTO settlements (
            merchant_id,
            reference,
            amount,
            currency
        )
        VALUES (?, ?, ?, ?)
        """, (
            merchant_id,
            settlement.get("reference"),
            settlement.get("amount"),
            settlement.get("currency")
        ))

        self.db.commit()

        return settlement

    def list(self, merchant_id):
        cursor = self.db.cursor()

        cursor.execute("""
        SELECT
            merchant_id,
            reference,
            amount,
            currency
        FROM settlements
        WHERE merchant_id = ?
        ORDER BY rowid ASC
        """, (merchant_id,))

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def clear(self):
        cursor = self.db.cursor()

        cursor.execute(
            "DELETE FROM settlements"
        )

        self.db.commit()
