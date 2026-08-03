import uuid
import secrets


class MerchantService:
    """
    In-memory merchant service.
    Will later be replaced with database persistence.
    """

    def __init__(self):
        self._merchants = {}

    def create_merchant(self, data):
        merchant_id = str(uuid.uuid4())

        merchant = {
            "merchant_id": merchant_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "status": "active",
            "api_key": self.generate_api_key(),
        }

        self._merchants[merchant_id] = merchant

        return merchant

    def list_merchants(self):
        return list(self._merchants.values())

    def get_merchant(self, merchant_id):
        return self._merchants.get(merchant_id)


    def generate_api_key(self):
        return secrets.token_hex(32)


    def find_by_api_key(self, api_key):
        for merchant in self._merchants.values():
            if merchant.get("api_key") == api_key:
                return merchant
        return None

    def authenticate(self, api_key):
        merchant = self.find_by_api_key(api_key)

        if merchant is None:
            return None

        if merchant.get("status") != "active":
            return None

        return merchant


    def create(self, **data):
        return self.create_merchant(data)

    def rotate_api_key(self, merchant_id):
        merchant = self.get_merchant(merchant_id)

        if merchant is None:
            return None

        merchant["api_key"] = self.generate_api_key()

        return merchant
