import unittest
import httpretty
from wowvideosplitter import get_report_time, get_report_fight_times

class TestWCL(unittest.TestCase):
    @httpretty.activate
    def test_get_report_time(self):
        response = '''
some text
var start_time = 123;
var end_time = 456;
more text
        '''
        httpretty.register_uri(httpretty.GET, 'https://www.warcraftlogs.com/reports/test', body=response)
        start_time, end_time = get_report_time('test')
        self.assertEqual(start_time, 123)
        self.assertEqual(end_time, 456)

    @httpretty.activate
    def test_get_report_fight_times(self):
        response = '''
{
    "fights": [
        {
            "id": 1,
            "start_time": 1,
            "end_time": 2,
            "boss": 1
        },
        {
            "id": 2,
            "start_time": 3,
            "end_time": 4
        },
        {
            "id": 3,
            "start_time": 10,
            "end_time": 20,
            "boss": 1
        }
    ]
}
        '''
        httpretty.register_uri(httpretty.GET, 'https://www.warcraftlogs.com/v1/report/fights/report?api_key=key', body=response)
        boss_fights = get_report_fight_times('key', 'report')
        all_fights = get_report_fight_times('key', 'report', False)
        self.assertEqual(boss_fights, [
            {
                'id': 1,
                'start_time': 1,
                'end_time': 2
            },
            {
                'id': 3,
                'start_time': 10,
                'end_time': 20
            }
        ])

        self.assertEqual(all_fights, [
            {
                'id': 1,
                'start_time': 1,
                'end_time': 2
            },
            {
                'id': 2,
                'start_time': 3,
                'end_time': 4
            },
            {
                'id': 3,
                'start_time': 10,
                'end_time': 20
            }
        ])
