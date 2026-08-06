import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class SwiftEngineTestCase(unittest.TestCase):
    """Base class for all Swift Payment Engine tests."""
    pass
