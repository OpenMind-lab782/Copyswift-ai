import os
import unittest
from unittest.mock import patch

from payment_engine.factory import RepositoryFactory
from payment_engine.repositories.postgres_payment_repository import (
    PostgreSQLPaymentRepository,
)
from payment_engine.repositories.postgres_payment_event_repository import (
    PostgreSQLPaymentEventRepository,
)
from payment_engine.repositories.sqlite_payment_repository import (
    SQLitePaymentRepository,
)
from payment_engine.repositories.sqlite_payment_event_repository import (
    SQLitePaymentEventRepository,
)

from payment_engine.repositories.postgres_settlement_repository import (
    PostgreSQLSettlementRepository,
)
from payment_engine.repositories.postgres_reconciliation_repository import (
    PostgreSQLReconciliationRepository,
)
from payment_engine.repositories.postgres_reconciliation_report_repository import (
    PostgreSQLReconciliationReportRepository,
)
from payment_engine.repositories.sqlite_settlement_repository import (
    SQLiteSettlementRepository,
)
from payment_engine.repositories.sqlite_reconciliation_repository import (
    SQLiteReconciliationRepository,
)
from payment_engine.repositories.sqlite_reconciliation_report_repository import (
    SQLiteReconciliationReportRepository,
)


class RepositoryFactoryTests(unittest.TestCase):

    def tearDown(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

    def test_sqlite_default_payment_repository(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

        repo = RepositoryFactory.payment_repository()

        self.assertIsInstance(
            repo,
            SQLitePaymentRepository,
        )

    def test_postgres_payment_repository(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        with patch(
            "payment_engine.factory.repository_factory."
            "PostgreSQLPaymentRepository"
        ) as repository_class:

            repository_class.return_value = object()

            repo = RepositoryFactory.payment_repository()

            repository_class.assert_called_once()

            self.assertIs(
                repo,
                repository_class.return_value,
            )

    def test_sqlite_default_event_repository(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

        repo = RepositoryFactory.payment_event_repository()

        self.assertIsInstance(
            repo,
            SQLitePaymentEventRepository,
        )

    def test_postgres_event_repository(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        with patch(
            "payment_engine.factory.repository_factory."
            "PostgreSQLPaymentEventRepository"
        ) as repository_class:

            repository_class.return_value = object()

            repo = RepositoryFactory.payment_event_repository()

            repository_class.assert_called_once()

            self.assertIs(
                repo,
                repository_class.return_value,
            )


    def test_sqlite_default_settlement_repository(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

        repo = RepositoryFactory.settlement_repository()

        self.assertIsInstance(
            repo,
            SQLiteSettlementRepository,
        )

    def test_postgres_settlement_repository(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        with patch(
            "payment_engine.factory.repository_factory."
            "PostgreSQLSettlementRepository"
        ) as repository_class:

            repository_class.return_value = object()

            repo = RepositoryFactory.settlement_repository()

            repository_class.assert_called_once()

            self.assertIs(
                repo,
                repository_class.return_value,
            )

    def test_sqlite_default_reconciliation_repository(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

        repo = RepositoryFactory.reconciliation_repository()

        self.assertIsInstance(
            repo,
            SQLiteReconciliationRepository,
        )

    def test_postgres_reconciliation_repository(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        with patch(
            "payment_engine.factory.repository_factory."
            "PostgreSQLReconciliationRepository"
        ) as repository_class:

            repository_class.return_value = object()

            repo = RepositoryFactory.reconciliation_repository()

            repository_class.assert_called_once()

            self.assertIs(
                repo,
                repository_class.return_value,
            )

    def test_sqlite_default_reconciliation_report_repository(self):
        os.environ.pop(
            "SWIFT_DB_BACKEND",
            None,
        )

        repo = RepositoryFactory.reconciliation_report_repository()

        self.assertIsInstance(
            repo,
            SQLiteReconciliationReportRepository,
        )

    def test_postgres_reconciliation_report_repository(self):
        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        with patch(
            "payment_engine.factory.repository_factory."
            "PostgreSQLReconciliationReportRepository"
        ) as repository_class:

            repository_class.return_value = object()

            repo = RepositoryFactory.reconciliation_report_repository()

            repository_class.assert_called_once()

            self.assertIs(
                repo,
                repository_class.return_value,
            )


if __name__ == "__main__":
    unittest.main()
