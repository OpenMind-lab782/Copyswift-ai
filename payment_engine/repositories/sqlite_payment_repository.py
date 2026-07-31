from payment_engine.database.sqlite import db


class SQLitePaymentRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, payment):
        cursor = self.db.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO payments (
            reference,
            merchant_id,
            amount,
            currency,
            status,
            gateway,
            customer_email,
            metadata
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payment.get("reference"),
            payment.get("merchant_id"),
            payment.get("amount"),
            payment.get("currency"),
            payment.get("status"),
            payment.get("gateway"),
            payment.get("customer_email"),
            str(payment.get("metadata", {}))
        ))

        self.db.commit()
        return payment

    def get(self, reference):
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT * FROM payments WHERE reference = ?",
            (reference,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def list(self):
        cursor = self.db.cursor()

        cursor.execute("SELECT * FROM payments")

        return [dict(row) for row in cursor.fetchall()]

    def update_status(self, reference, status):
        cursor = self.db.cursor()

        cursor.execute(
            "UPDATE payments SET status = ? WHERE reference = ?",
            (status, reference)
        )

        self.db.commit()

        return self.get(reference)
