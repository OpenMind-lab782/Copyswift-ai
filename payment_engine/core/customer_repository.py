"""
Customer Repository
"""

from payment_engine.core.customer import Customer


class CustomerRepository:
    """
    Simple in-memory customer repository.
    This will later be backed by SQLite/PostgreSQL.
    """

    def __init__(self):
        self._customers = {}

    def save(self, customer: Customer):
        self._customers[customer.email] = customer

    def get(self, email):
        return self._customers.get(email)

    def exists(self, email):
        return email in self._customers

    def all(self):
        return list(self._customers.values())
