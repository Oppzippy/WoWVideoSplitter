import unittest
import httpretty
from wowvideosplitter import WCLReport

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
        report = WCLReport('key', 'test')
        start_time, end_time = report.get_time_bounds()
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
        report = WCLReport('key', 'report')
        boss_fights = report.get_fight_times()
        all_fights = report.get_fight_times(bosses_only=False)
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
