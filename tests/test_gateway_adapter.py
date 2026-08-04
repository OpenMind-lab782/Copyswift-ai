import unittest

from payment_engine.gateway.adapter import GatewayAdapter


class GatewayAdapterTests(unittest.TestCase):

    def test_adapter_exposes_required_methods(self):

        adapter = GatewayAdapter()

        for method in (
            "initialize_payment",
            "verify_payment",
            "refund_payment",
        ):
            self.assertTrue(
                hasattr(adapter, method)
            )

    def test_methods_raise_not_implemented(self):

        adapter = GatewayAdapter()

        with self.assertRaises(NotImplementedError):
            adapter.initialize_payment({})

        with self.assertRaises(NotImplementedError):
            adapter.verify_payment("PAY-001")

        with self.assertRaises(NotImplementedError):
            adapter.refund_payment("PAY-001")


if __name__ == "__main__":
    unittest.main()
