class PaymentEngine:
    def __init__(self):
        self.version="1.0.0"

    def info(self):
        return {
            "name":"Swift Payment Engine",
            "version":self.version
        }
