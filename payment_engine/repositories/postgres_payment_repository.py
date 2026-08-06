class PostgreSQLPaymentRepository:
    """
    Placeholder PostgreSQL repository.

    This implementation will be expanded in the
    next feature batches with live database support.
    """

    def save(self, payment):
        raise NotImplementedError(
            "PostgreSQL repository not implemented yet."
        )

    def get(self, reference):
        raise NotImplementedError(
            "PostgreSQL repository not implemented yet."
        )

    def list(self):
        raise NotImplementedError(
            "PostgreSQL repository not implemented yet."
        )

    def update_status(self, reference, status):
        raise NotImplementedError(
            "PostgreSQL repository not implemented yet."
        )
