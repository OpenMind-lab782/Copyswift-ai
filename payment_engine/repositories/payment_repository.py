class PaymentRepository:

    def __init__(self):
        self._payments = {}

    def save(self, payment):
        self._payments[payment["reference"]] = payment
        return payment

    def get(self, reference):
        return self._payments.get(reference)

    def list(self):
        return list(self._payments.values())

    def clear(self):
        self._payments.clear()

    def update_status(self, reference, status):
        payment = self._payments.get(reference)

        if payment is None:
            return None

        payment["status"] = status
        return payment
