from payment_engine.database.sqlite import db


class SQLitePaymentRepository:

    def __init__(self, database=None):
        self.db = database or db

    def save(self, payment, connection=None):
        owns_connection = connection is None
        connection = connection or self.db.connection
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO payments (
                reference,
                merchant_id,
                amount,
                currency,
                status,
                gateway,
                customer_email,
                metadata,
                idempotency_key
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payment.get("reference"),
                payment.get("merchant_id"),
                payment.get("amount"),
                payment.get("currency"),
                payment.get("status"),
                payment.get("gateway"),
                payment.get("customer_email"),
                str(payment.get("metadata", {})),
                payment.get("idempotency_key"),
            ),
        )

        if owns_connection:
            self.db.commit()

        return payment

    def get(self, reference):
        cursor = self.db.cursor()

        cursor.execute(
            "SELECT * FROM payments WHERE reference = ?",
            (reference,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def find_by_idempotency_key(self, merchant_id, key):
        if not merchant_id or not key:
            return None

        cursor = self.db.cursor()

        cursor.execute(
            """
            SELECT *
            FROM payments
            WHERE merchant_id = ?
              AND idempotency_key = ?
            LIMIT 1
            """,
            (merchant_id, key),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        payment = dict(row)

        if isinstance(payment.get("metadata"), str):
            import json

            try:
                payment["metadata"] = json.loads(
                    payment["metadata"]
                )
            except (TypeError, ValueError):
                payment["metadata"] = {}

        return payment

    def list(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM payments")
        return [dict(row) for row in cursor.fetchall()]

    def update_status(self, reference, status, connection=None):
        owns_connection = connection is None
        connection = connection or self.db.connection
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE payments SET status = ? WHERE reference = ?",
            (status, reference),
        )

        if owns_connection:
            self.db.commit()

        return self.get(reference)

    def clear(self):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM payments")
        self.db.commit()
