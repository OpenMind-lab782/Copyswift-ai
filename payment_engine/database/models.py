from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone

from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    gateway = Column(
        String(50),
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="USD",
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending",
    )

    customer_id = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
