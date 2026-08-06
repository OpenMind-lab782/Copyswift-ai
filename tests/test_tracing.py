import unittest

from payment_engine.tracing import CorrelationId


class TestCorrelationId(unittest.TestCase):

    def test_generates_string(self):
        cid = CorrelationId.new()
        self.assertIsInstance(cid, str)

    def test_generates_unique_values(self):
        a = CorrelationId.new()
        b = CorrelationId.new()
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
