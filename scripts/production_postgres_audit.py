import os
import sys

from sqlalchemy import create_engine, inspect, text

REQUIRED_TABLES = (
    "payments",
    "payment_events",
    "settlements",
    "reconciliation_records",
    "reconciliation_report_records",
)
def database_url():
    value = os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is not configured")
    if value.startswith("postgres://"):
        value = "postgresql+psycopg://" + value[len("postgres://"):]
    elif value.startswith("postgresql://"):
        value = "postgresql+psycopg://" + value[len("postgresql://"):]
    if not value.startswith("postgresql+psycopg://"):
        raise RuntimeError("DATABASE_URL must use PostgreSQL with psycopg 3")
    return value

def audit():
    engine = create_engine(database_url(), future=True, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("BEGIN READ ONLY"))
            try:
                identity = connection.execute(text("SELECT current_database(), current_user, current_setting('server_version' )")).one()
                inspector = inspect(connection)
                tables = inspector.get_table_names()
                missing = [name for name in REQUIRED_TABLES if name not in tables]
                print("DATABASE:", identity[0])
                print("POSTGRESQL:", identity[2])
                print("TABLES FOUND:", len(tables))
                print("TABLE NAMES:", ", ".join(sorted(tables)))
                print("REQUIRED TABLES:", len(REQUIRED_TABLES))
                if missing:
                    raise RuntimeError("Missing required tables: " + ", ".join(missing))
                for name in REQUIRED_TABLES:
                    columns = inspector.get_columns(name)
                    print("TABLE:", name, "COLUMNS:", len(columns))
            finally:
                connection.execute(text("ROLLBACK"))
    finally:
        engine.dispose()

if __name__ == "__main__":
    try:
        audit()
    except Exception as exc:
        print("AUDIT FAILED:", type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        sys.exit(1)
    print("AUDIT PASSED")
