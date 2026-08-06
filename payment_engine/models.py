from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class PaymentRequest:
    gateway: str
    amount: float
    currency: str
    customer: str
    reference: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentResponse:
    success: bool
    status: str
    message: str
    reference: str = ""
    gateway: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
