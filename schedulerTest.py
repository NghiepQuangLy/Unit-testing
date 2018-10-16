import unittest
from scheduler import Scheduler
from scheduler import Satellite
from scheduler import IllegalArgumentException
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import pytz


class SatelliteTest(unittest.TestCase):
    """ Tests for the Satellite class. """

    def setUp(self):
        self.satellite = Satellite("name", "info")

    def test_is_visible_invalid(self):
        with self.assertRaises(IllegalArgumentException):
            self.satellite.is_visible(None)


class Alt:
    """ ??? """

    def __init__(self, alt):
        self.degrees = alt


class SchedulerTest(unittest.TestCase):
    """
    Tests for the scheduler class. Add more tests
    to test the code that you write.
    """

    def setUp(self):
        self.scheduler = Scheduler()

    def test_its_alive(self):
        (stime, satellites) = self.scheduler.find_time()
        self.assertTrue(type(stime) == type(datetime.now()))

    def test_find_time_start_time_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(start_time="now")

    def test_find_time_duration_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(duration='a')

    def test_find_time_duration_non_positive(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(duration=-1)

    def test_find_time_n_windows_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(n_windows='a')

    def test_find_time_n_windows_non_positive(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(n_windows=0)

    def test_find_time_sample_interval_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(sample_interval='a')

    def test_find_time_sample_interval_non_positive(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(sample_interval=0)

    def test_find_time_sample_interval_bigger_than_duration(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(sample_interval=70, duration=60)

    def test_find_time_location_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location='a')

    def test_find_time_location_invalid_list_or_tuple(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location=(1, 2, 3))

    def test_find_time_location_latitude_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location=('a', 0))

    def test_find_time_location_latitude_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location=(-100, 0))

    def test_find_time_location_longitude_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location=(0, 'a'))

    def test_find_time_location_longitude_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location=(0, 200))

    def test_find_time_cumulative_non_boolean(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(cumulative = 10)

    def test_satellites_list_to_satellites_name_list_non_satellite(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.satellites_list_to_satellites_name_list([True, None])

    def test_get_all_satellites_invalid_url(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.get_all_satellites("invalid_url")

    @patch.object(Satellite, "get_altitude")
    def test_find_visible_satellites_instance(self, mock_get_altitude):
        satellites_list = [Satellite('sat_1', None),
                           Satellite('sat_2', None),
                           Satellite('sat_3', None),
                           Satellite('sat_4', None)]
        mock_get_altitude.side_effect = [Alt(10), Alt(-10), Alt(-10), Alt(10)]
        visible_satellites = self.scheduler.find_visible_satellites_instance(satellites_list, None, None)
        assert([visible_satellites[0].name == 'sat_1'])
        assert([visible_satellites[1].name == 'sat_4'])

    @patch.object(Scheduler, "find_visible_satellites_instance")
    def test_find_max_visible_satellites_interval_non_cumulative(self, mock_find_visible_satellites_instance):
        mock_find_visible_satellites_instance.side_effect = [['sat_1'], ['sat_1', 'sat_2']]

        timezone = pytz.timezone("UTC")
        start_time = timezone.localize(datetime(2018, 1, 1, 10, 0, 0))

        interval_start_time, visible_sats = self.scheduler.find_max_visible_satellites_interval_non_cumulative(
            [None], None, start_time, 120, 60)
        assert(interval_start_time.utc_datetime() == start_time + timedelta(hours=1))
        assert(visible_sats == ['sat_1', 'sat_2'])

    @patch.object(Scheduler, "find_visible_satellites_instance")
    def test_find_max_visible_satellites_interval_cumulative(self, mock_find_visible_satellites_instance):
        mock_find_visible_satellites_instance.side_effect = [['sat_1', 'sat_2'], ['sat_2', 'sat_3']]

        timezone = pytz.timezone("UTC")
        start_time = timezone.localize(datetime(2018, 1, 1, 10, 0, 0))

        interval_start_time, visible_sats = self.scheduler.find_max_visible_satellites_interval_cumulative(
            [None], None, start_time, 120, 60)
        assert(interval_start_time.utc_datetime() == start_time)
        assert(len(visible_sats) == 3)


if __name__ == "__main__":
    unittest.main()
