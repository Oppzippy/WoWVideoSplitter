import unittest
from wowvideosplitter import clamp

class TestUtil(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(5, 3, 6), 5)
        self.assertEqual(clamp(0, 3, 6), 3)
        self.assertEqual(clamp(9, 3, 6), 6)
