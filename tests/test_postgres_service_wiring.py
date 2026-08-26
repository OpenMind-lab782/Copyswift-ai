import os
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine

from payment_engine.database.postgres import PostgreSQLDatabase
from payment_engine.database.postgres_schema import initialize_postgres_schema
from payment_engine.services.settlement_service import SettlementService
from payment_engine.services.reconciliation_service import ReconciliationService
from payment_engine.services.reconciliation_report_service import (
    ReconciliationReportService,
)


class PostgreSQLServiceWiringTests(unittest.TestCase):

    def setUp(self):
        self.original_backend = os.environ.get(
            "SWIFT_DB_BACKEND"
        )

        os.environ["SWIFT_DB_BACKEND"] = "postgres"

        self.engine = create_engine(
            "sqlite:///:memory:",
            future=True,
        )

        self.database = PostgreSQLDatabase(
            database_url="sqlite:///:memory:",
            engine=self.engine,
        )

        initialize_postgres_schema(self.database)

    def tearDown(self):
        self.database.dispose()

        if self.original_backend is None:
            os.environ.pop(
                "SWIFT_DB_BACKEND",
                None,
            )
        else:
            os.environ["SWIFT_DB_BACKEND"] = (
                self.original_backend
            )

    def test_settlement_service_uses_postgres_factory(self):
        with patch(
            "payment_engine.services.settlement_service."
            "RepositoryFactory.settlement_repository"
        ) as factory:

            factory.return_value = object()

            service = SettlementService()

            factory.assert_called_once()

            self.assertIs(
                service.repository,
                factory.return_value,
            )

    def test_reconciliation_service_uses_postgres_factory(self):
        with patch(
            "payment_engine.services.reconciliation_service."
            "RepositoryFactory.reconciliation_repository"
        ) as factory:

            factory.return_value = object()

            service = ReconciliationService()

            factory.assert_called_once()

            self.assertIs(
                service.repository,
                factory.return_value,
            )

    def test_reconciliation_report_service_uses_postgres_factory(self):
        with patch(
            "payment_engine.services.reconciliation_report_service."
            "RepositoryFactory.reconciliation_report_repository"
        ) as factory:

            factory.return_value = object()

            service = ReconciliationReportService()

            factory.assert_called_once()

            self.assertIs(
                service.repository,
                factory.return_value,
            )

    def test_settlement_service_persists_through_postgres_repository(self):
        from payment_engine.repositories.postgres_settlement_repository import (
            PostgreSQLSettlementRepository,
        )

        repository = PostgreSQLSettlementRepository(
            database=self.database
        )

        service = SettlementService(
            repository=repository
        )

        service.record(
            merchant_id="merchant-001",
            reference="SETTLE-SVC-001",
            amount=5000,
            currency="NGN",
        )

        rows = service.list(
            "merchant-001"
        )

        self.assertEqual(
            len(rows),
            1,
        )

        self.assertEqual(
            rows[0]["reference"],
            "SETTLE-SVC-001",
        )

    def test_reconciliation_service_persists_through_postgres_repository(self):
        from payment_engine.repositories.postgres_reconciliation_repository import (
            PostgreSQLReconciliationRepository,
        )

        repository = PostgreSQLReconciliationRepository(
            database=self.database
        )

        service = ReconciliationService(
            repository=repository
        )

        service.record(
            merchant_id="merchant-001",
            reference="REC-SVC-001",
        )

        rows = service.list(
            "merchant-001"
        )

        self.assertEqual(
            len(rows),
            1,
        )

        self.assertEqual(
            rows[0]["reference"],
            "REC-SVC-001",
        )

    def test_reconciliation_report_service_persists_through_postgres_repository(self):
        from payment_engine.repositories.postgres_reconciliation_report_repository import (
            PostgreSQLReconciliationReportRepository,
        )

        repository = PostgreSQLReconciliationReportRepository(
            database=self.database
        )

        service = ReconciliationReportService(
            repository=repository
        )

        service.record(
            merchant_id="merchant-001",
            reference="REPORT-SVC-001",
            amount=12500,
            currency="BWP",
        )

        report = service.generate(
            "merchant-001"
        )

        self.assertEqual(
            report["total_transactions"],
            1,
        )

        self.assertEqual(
            report["total_amount"],
            12500,
        )

        self.assertEqual(
            report["transactions"][0]["reference"],
            "REPORT-SVC-001",
        )


if __name__ == "__main__":
    unittest.main()
