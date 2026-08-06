from sqlalchemy import Column, Integer, String, Boolean
from payment_engine.database.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, unique=True)
    email = Column(String(200), nullable=False)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return (
            f"<Merchant(name={self.name}, "
            f"email={self.email}, "
            f"active={self.active})>"
        )
