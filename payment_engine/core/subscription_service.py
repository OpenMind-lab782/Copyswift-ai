"""
Subscription Service
"""

from datetime import UTC, datetime, timedelta


class SubscriptionService:
    """
    Handles subscription lifecycle operations.
    """

    def activate(self, customer, plan):

        renewal = datetime.now(UTC) + timedelta(days=30)

        return {
            "customer": customer.email,
            "plan": plan,
            "status": "Active",
            "activated_at": datetime.now(UTC).isoformat(),
            "renewal_date": renewal.date().isoformat(),
        }

    def upgrade(self, customer, plan):

        customer.subscription = plan

        return {
            "customer": customer.email,
            "subscription": customer.subscription,
            "status": customer.status,
        }

    def cancel(self, customer):

        customer.status = "Cancelled"

        return {
            "customer": customer.email,
            "status": customer.status,
        }
