import json

from sqlalchemy import text

from payment_engine.database.postgres import PostgreSQLDatabase


class PostgreSQLPaymentRepository:
    """
    Persistent PostgreSQL payment repository.

    The repository depends on the PostgreSQLDatabase abstraction rather
    than directly depending on psycopg. This keeps the repository
    testable and allows SQLAlchemy to manage the PostgreSQL driver.
    """

    def __init__(self, database=None):
        # Schema provisioning is an explicit deployment/bootstrap concern.
        # Repository construction must never mutate the production schema.
        self.db = database or PostgreSQLDatabase()

    @staticmethod
    def _serialize_metadata(metadata):
        if metadata is None:
            return "{}"

        return json.dumps(metadata)

    @staticmethod
    def _deserialize_metadata(metadata):
        if not metadata:
            return {}

        if isinstance(metadata, dict):
            return metadata

        try:
            return json.loads(metadata)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def _row_to_payment(cls, row):
        if row is None:
            return None

        payment = dict(row)

        payment["metadata"] = cls._deserialize_metadata(
            payment.get("metadata")
        )

        return payment

    def save(self, payment):
        statement = text(
            """
            INSERT INTO payments (
                reference,
                merchant_id,
                amount,
                currency,
                status,
                gateway,
                customer_email,
                metadata,
                idempotency_key,
                idempotency_fingerprint,
                created_at,
                updated_at
            )
            VALUES (
                :reference,
                :merchant_id,
                :amount,
                :currency,
                :status,
                :gateway,
                :customer_email,
                :metadata,
                :idempotency_key,
                :idempotency_fingerprint,
                :created_at,
                :updated_at
            )
            ON CONFLICT (reference)
            DO UPDATE SET
                merchant_id = EXCLUDED.merchant_id,
                amount = EXCLUDED.amount,
                currency = EXCLUDED.currency,
                status = EXCLUDED.status,
                gateway = EXCLUDED.gateway,
                customer_email = EXCLUDED.customer_email,
                metadata = EXCLUDED.metadata,
                idempotency_key = EXCLUDED.idempotency_key,
                idempotency_fingerprint = EXCLUDED.idempotency_fingerprint,
                updated_at = EXCLUDED.updated_at
            """
        )

        parameters = {
            "reference": payment.get("reference"),
            "merchant_id": payment.get("merchant_id"),
            "amount": payment.get("amount"),
            "currency": payment.get("currency"),
            "status": payment.get("status"),
            "gateway": payment.get("gateway"),
            "customer_email": payment.get("customer_email"),
            "metadata": self._serialize_metadata(
                payment.get("metadata", {})
            ),
            "idempotency_key": payment.get("idempotency_key"),
            "idempotency_fingerprint": payment.get("idempotency_fingerprint"),
            "created_at": payment.get("created_at"),
            "updated_at": payment.get("updated_at"),
        }

        with self.db.engine.begin() as connection:
            connection.execute(statement, parameters)

        return payment

    def get(self, reference):
        statement = text(
            """
            SELECT
                reference,
                merchant_id,
                amount,
                currency,
                status,
                gateway,
                customer_email,
                metadata,
                idempotency_key,
                idempotency_fingerprint,
                created_at,
                updated_at
            FROM payments
            WHERE reference = :reference
            """
        )

        with self.db.connect() as connection:
            row = connection.execute(
                statement,
                {"reference": reference},
            ).mappings().first()

        return self._row_to_payment(row)

    def find_by_idempotency_key(self, merchant_id, key):
        if not merchant_id or not key:
            return None

        statement = text(
            """
            SELECT
                reference,
                merchant_id,
                amount,
                currency,
                status,
                gateway,
                customer_email,
                metadata,
                idempotency_key,
                idempotency_fingerprint,
                created_at,
                updated_at
            FROM payments
            WHERE merchant_id = :merchant_id
              AND idempotency_key = :idempotency_key
            LIMIT 1
            """
        )

        with self.db.connect() as connection:
            row = connection.execute(
                statement,
                {
                    "merchant_id": merchant_id,
                    "idempotency_key": key,
                },
            ).mappings().first()

        return self._row_to_payment(row)

    def list(self):
        statement = text(
            """
            SELECT
                reference,
                merchant_id,
                amount,
                currency,
                status,
                gateway,
                customer_email,
                metadata,
                idempotency_key,
                idempotency_fingerprint,
                created_at,
                updated_at
            FROM payments
            ORDER BY created_at ASC, reference ASC
            """
        )

        with self.db.connect() as connection:
            rows = connection.execute(statement).mappings().all()

        return [
            self._row_to_payment(row)
            for row in rows
        ]

    def update_status(self, reference, status):
        statement = text(
            """
            UPDATE payments
            SET
                status = :status,
                updated_at = CURRENT_TIMESTAMP
            WHERE reference = :reference
            """
        )

        with self.db.engine.begin() as connection:
            result = connection.execute(
                statement,
                {
                    "reference": reference,
                    "status": status,
                },
            )

        if result.rowcount == 0:
            return None

        return self.get(reference)

    def clear(self):
        statement = text("DELETE FROM payments")

        with self.db.engine.begin() as connection:
            connection.execute(statement)
