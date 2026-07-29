from payment_engine.database.merchant_repository import MerchantRepository


class MerchantService:

    def __init__(self):
        self.repository = MerchantRepository()

    def register_merchant(self, name, email):
        existing = self.repository.get_by_name(name)

        if existing:
            raise ValueError(f"Merchant '{name}' already exists.")

        return self.repository.create(name, email)

    def get_merchant(self, name):
        return self.repository.get_by_name(name)

    def list_merchants(self):
        return self.repository.list_all()
