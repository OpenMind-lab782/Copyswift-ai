from sqlalchemy import text
from sqlalchemy.exc import NoInspectionAvailable


PAYMENTS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS payments (
    reference VARCHAR(100) PRIMARY KEY,
    merchant_id VARCHAR(100),
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(30) NOT NULL,
    gateway VARCHAR(50),
    customer_email VARCHAR(255),
    metadata TEXT,
    idempotency_key VARCHAR(255),
    idempotency_fingerprint VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

PAYMENT_EVENTS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS payment_events (
    id SERIAL PRIMARY KEY,
    reference VARCHAR(100) NOT NULL,
    event VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    timestamp TIMESTAMP NULL,
    metadata TEXT
)
"""

SETTLEMENTS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS settlements (
    id SERIAL PRIMARY KEY,
    merchant_id VARCHAR(100) NOT NULL,
    reference VARCHAR(100) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) NOT NULL
)
"""

RECONCILIATION_RECORDS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reconciliation_records (
    id SERIAL PRIMARY KEY,
    merchant_id VARCHAR(100) NOT NULL,
    reference VARCHAR(100) NOT NULL
)
"""

RECONCILIATION_REPORT_RECORDS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reconciliation_report_records (
    id SERIAL PRIMARY KEY,
    merchant_id VARCHAR(100) NOT NULL,
    reference VARCHAR(100) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) NOT NULL
)
"""


def initialize_postgres_schema(database):
    """
    Create or upgrade the core Swift Payment Engine database schema.

    PostgreSQL remains the production target, while the test suite may
    inject SQLite engines into the PostgreSQL database adapter. Schema
    upgrades therefore use SQLAlchemy dialect detection instead of
    PostgreSQL-only ALTER syntax on every backend.
    """
    statements = (
        PAYMENTS_SCHEMA_SQL,
        PAYMENT_EVENTS_SCHEMA_SQL,
        SETTLEMENTS_SCHEMA_SQL,
        RECONCILIATION_RECORDS_SCHEMA_SQL,
        RECONCILIATION_REPORT_RECORDS_SCHEMA_SQL,
    )

    with database.engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

        try:
            inspector = __import__("sqlalchemy").inspect(connection)
        except NoInspectionAvailable:
            # Architecture/unit tests may inject MagicMock databases.
            # The explicit initializer must remain callable without
            # forcing SQLAlchemy reflection against a mock object.
            return

        payment_columns = {
            column["name"]
            for column in inspector.get_columns("payments")
        }

        if "idempotency_fingerprint" not in payment_columns:
            connection.execute(
                text(
                    "ALTER TABLE payments "
                    "ADD COLUMN idempotency_fingerprint VARCHAR(64)"
                )
            )

        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "uq_payments_merchant_idempotency "
                "ON payments (merchant_id, idempotency_key)"
            )
        )
