from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any


VALID_STATUSES = (
    "pending",
    "processing",
    "verified",
    "activated",
    "failed",
    "cancelled",
)


@dataclass
class Transaction:

    gateway: str
    amount: float
    currency: str
    customer: str

    reference: str = ""
    transaction_id: str = field(default_factory=lambda: uuid4().hex)

    status: str = "pending"

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_status(self, status: str):

        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid transaction status: {status}")

        self.status = status

    def as_dict(self):

        return {
            "transaction_id": self.transaction_id,
            "gateway": self.gateway,
            "reference": self.reference,
            "customer": self.customer,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
