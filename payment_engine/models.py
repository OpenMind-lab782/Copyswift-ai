from dataclasses import dataclass
from typing import Optional

@dataclass
class PaymentRequest:
    amount: float
    currency: str
    customer: str
    gateway: Optional[str] = None

@dataclass
class PaymentResponse:
    success: bool
    reference: str
    message: str
