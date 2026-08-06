import unittest
import time

from payment_engine.latency import LatencyRecorder, Timer


class TestLatency(unittest.TestCase):

    def test_record_latency(self):
        recorder = LatencyRecorder()
        recorder.record("paystack", 0.10)
        recorder.record("paystack", 0.20)

        self.assertEqual(recorder.count("paystack"), 2)
        self.assertAlmostEqual(
            recorder.average("paystack"),
            0.15,
            places=6,
        )

    def test_timer(self):
        with Timer() as timer:
            time.sleep(0.01)

        self.assertGreater(timer.elapsed, 0)


if __name__ == "__main__":
    unittest.main()
