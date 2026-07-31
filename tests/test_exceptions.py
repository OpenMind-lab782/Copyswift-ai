from tests.base import SwiftEngineTestCase

from payment_engine.exceptions import (
    SwiftPaymentError,
    PaymentError,
    GatewayError,
    MerchantError,
    RepositoryError,
    TransactionError,
    ValidationError,
)


class ExceptionFrameworkTests(SwiftEngineTestCase):

    def test_payment_error(self):
        self.assertTrue(issubclass(PaymentError, SwiftPaymentError))

    def test_gateway_error(self):
        self.assertTrue(issubclass(GatewayError, SwiftPaymentError))

    def test_merchant_error(self):
        self.assertTrue(issubclass(MerchantError, SwiftPaymentError))

    def test_repository_error(self):
        self.assertTrue(issubclass(RepositoryError, SwiftPaymentError))

    def test_transaction_error(self):
        self.assertTrue(issubclass(TransactionError, SwiftPaymentError))

    def test_validation_error(self):
        self.assertTrue(issubclass(ValidationError, SwiftPaymentError))


if __name__ == "__main__":
    import unittest
    unittest.main()
