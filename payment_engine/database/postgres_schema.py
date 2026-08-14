from sqlalchemy import text


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
    Create the core Swift Payment Engine PostgreSQL tables.

    This function is deliberately explicit instead of relying on SQLite
    migration syntax so that PostgreSQL remains a first-class backend.
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
