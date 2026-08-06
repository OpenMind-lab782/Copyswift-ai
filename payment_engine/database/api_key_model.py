from sqlalchemy import Column, Integer, String, Boolean
from payment_engine.database.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)

    application = Column(
        String(120),
        nullable=False
    )

    api_key = Column(
        String(128),
        unique=True,
        nullable=False
    )

    active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<APIKey(application={self.application}, "
            f"active={self.active})>"
        )
