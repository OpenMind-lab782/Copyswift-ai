class CryptoPaymentService:

    def __init__(self):
        self._payments = {}

    def submit(self, reference, data):
        self._payments[reference] = {
            "status": "pending",
            **data,
        }
        return self._payments[reference]

    def activate(self, reference):
        if reference not in self._payments:
            return None

        self._payments[reference]["status"] = "activated"
        return self._payments[reference]

    def reject(self, reference):
        if reference not in self._payments:
            return None

        self._payments[reference]["status"] = "rejected"
        return self._payments[reference]

    def get(self, reference):
        return self._payments.get(reference)
