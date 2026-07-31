import unittest

from payment_engine.request import generate_request_id


class RequestIdTests(unittest.TestCase):

    def test_request_id_is_string(self):
        request_id = generate_request_id()
        self.assertIsInstance(request_id, str)

    def test_request_ids_are_unique(self):
        id1 = generate_request_id()
        id2 = generate_request_id()

        self.assertNotEqual(id1, id2)


if __name__ == "__main__":
    unittest.main()
