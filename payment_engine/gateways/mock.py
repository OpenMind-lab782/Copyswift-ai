class MockGateway:
    name="mock"

    def charge(self,amount):
        return {
            "success":True,
            "amount":amount
        }
