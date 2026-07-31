from payment_engine.database.database import SessionLocal
from payment_engine.database.merchant_model import Merchant


class MerchantRepository:

    def create(self, name, email):
        session = SessionLocal()

        try:
            merchant = Merchant(
                name=name,
                email=email
            )

            session.add(merchant)
            session.commit()
            session.refresh(merchant)

            return merchant

        finally:
            session.close()

    def get_by_name(self, name):
        session = SessionLocal()

        try:
            return (
                session.query(Merchant)
                .filter(Merchant.name == name)
                .first()
            )

        finally:
            session.close()

    def list_all(self):
        session = SessionLocal()

        try:
            return session.query(Merchant).all()

        finally:
            session.close()
