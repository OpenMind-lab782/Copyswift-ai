class Assertions:

    @staticmethod
    def payment_saved(testcase, payment):

        testcase.assertIsNotNone(payment)
        testcase.assertIn("reference", payment)
        testcase.assertIn("status", payment)
