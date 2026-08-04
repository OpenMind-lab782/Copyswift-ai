"""
Dashboard Service
"""

from payment_engine.core.payment_history_service import PaymentHistoryService
from payment_engine.core.sqlite_customer_repository import SQLiteCustomerRepository


class DashboardService:

    def __init__(self):
        self.customers = SQLiteCustomerRepository()
        self.history = PaymentHistoryService()

    def summary(self, email):

        customer = self.customers.get(email)

        payments = [
            payment
            for payment in self.history.history()
            if payment[1] == email
        ]

        return {
            "customer": (
                customer.to_dict()
                if customer
                else None
            ),
            "payment_count": len(payments),
            "payments": payments,
        }
