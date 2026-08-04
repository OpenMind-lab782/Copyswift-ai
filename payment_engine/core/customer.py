"""
Customer Domain Model
"""


class Customer:
    """
    Represents a CopySwiftAI customer.
    """

    def __init__(
        self,
        name,
        email=None,
        subscription="Starter",
        status="Active",
    ):
        self.name = name
        self.email = email
        self.subscription = subscription
        self.status = status

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "subscription": self.subscription,
            "status": self.status,
        }
