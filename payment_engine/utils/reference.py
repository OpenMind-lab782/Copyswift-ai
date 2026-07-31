from datetime import datetime, timezone
from secrets import token_hex


class PaymentReference:

    PREFIX = "SWIFT"

    @classmethod
    def generate(cls):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random = token_hex(4).upper()

        return f"{cls.PREFIX}-{timestamp}-{random}"
