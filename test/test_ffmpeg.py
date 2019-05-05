import unittest
from wowvideosplitter import VideoSplitter

class TestFFmpeg(unittest.TestCase):
    def test_ms_to_time(self):
        self.assertEqual(VideoSplitter.ms_to_time(0), '0:00:00')
        self.assertEqual(VideoSplitter.ms_to_time(5000), '0:00:05')
        self.assertEqual(VideoSplitter.ms_to_time(72000), '0:01:12')
        self.assertEqual(VideoSplitter.ms_to_time(3601000), '1:00:01')
