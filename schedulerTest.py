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
        # TODO: mock valid Satellite info?
        self.satellite = Satellite("name", "info")

    def test_is_visible_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.satellite.is_visible(None)

    def test_is_visible_true(self):
        self.assertTrue(self.satellite.is_visible(10))

    def test_is_visible_false(self):
        self.assertFalse(self.satellite.is_visible(-10))


class TestingAlt:
    """ Class to allow for `.degree` in testing. """

    def __init__(self, alt):
        self.degrees = alt


class SchedulerTest(unittest.TestCase):
    """ Tests for the scheduler class. """

    def setUp(self):
        self.scheduler = Scheduler()

    def check_times_equal(self,time1,time2):
        time1_str = '{:%Y-%m-%d-%H-%M-%S:}'.format(time1)
        time2_str = '{:%Y-%m-%d-%H-%M-%S:}'.format(time2)
        if time1_str == time2_str:
            return True
        else:
            return False

    def test_its_alive(self):
        (stime, satellites) = self.scheduler.find_time()
        self.assertTrue(type(stime) == type(datetime.now()))
        self.assertTrue(len(satellites) > 0)

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

    def test_find_time_cumulative_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(cumulative=10)

    def test_satellites_list_to_satellites_name_list_empty_satellites_list(self):
        self.assertTrue(self.scheduler.satellites_list_to_satellites_name_list([]) == [])

    def test_satellites_list_to_satellites_name_list_non_satellite(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.satellites_list_to_satellites_name_list([True, None])

    def test_get_all_satellites_invalid_url(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.get_all_satellites("invalid_url")

    @patch.object(Scheduler, "find_max_visible_satellites_interval_cumulative")
    def test_find_time_cumulative_naive_time(self, mock_find_max_visible_satellites_interval_cumulative):
        timezone = pytz.timezone("UTC")
        time_copy = datetime.now()
        time = timezone.localize(time_copy)
        mock_values = [[time,[Satellite('sat_1',None),
                              Satellite('sat_2', None)]],
                       [time,[Satellite('sat_1', None),
                              Satellite('sat_2', None),
                              Satellite('sat_3', None)]]]
        mock_find_max_visible_satellites_interval_cumulative.side_effect = mock_values
        max_interval_start,max_interval_satellites = self.scheduler.find_time(start_time=time_copy, n_windows=2, cumulative=True)
        self.assertTrue(self.check_times_equal(max_interval_start, time + timedelta(hours=1)))
        self.assertTrue(len(max_interval_satellites) == 3)

    @patch.object(Scheduler, "find_max_visible_satellites_interval_cumulative")
    def test_find_time_cumulative_non_naive_time(self, mock_find_max_visible_satellites_interval_cumulative):
        timezone = pytz.timezone("UTC")
        time = timezone.localize(datetime.now())
        mock_values = [[time, [Satellite('sat_1', None),
                               Satellite('sat_2', None)]],
                       [time, [Satellite('sat_1', None),
                               Satellite('sat_2', None),
                               Satellite('sat_3', None)]]]
        mock_find_max_visible_satellites_interval_cumulative.side_effect = mock_values
        max_interval_start, max_interval_satellites = self.scheduler.find_time(start_time=time, n_windows=2,
                                                                               cumulative=True)
        self.assertTrue(self.check_times_equal(max_interval_start, time + timedelta(hours=1)))
        self.assertTrue(len(max_interval_satellites) == 3)

    @patch.object(Satellite, "get_altitude")
    def test_find_visible_satellites_instance(self, mock_get_altitude):
        satellites_list = [Satellite('sat_1', None),
                           Satellite('sat_2', None),
                           Satellite('sat_3', None),
                           Satellite('sat_4', None)]
        mock_get_altitude.side_effect = [TestingAlt(10), TestingAlt(-10), TestingAlt(-10), TestingAlt(10)]
        visible_satellites = self.scheduler.find_visible_satellites_instance(satellites_list, None, None)
        self.assertTrue([visible_satellites[0].name == 'sat_1'])
        self.assertTrue([visible_satellites[1].name == 'sat_4'])

    @patch.object(Scheduler, "find_visible_satellites_instance")
    def test_find_max_visible_satellites_interval_non_cumulative(self, mock_find_visible_satellites_instance):
        mock_find_visible_satellites_instance.side_effect = [['sat_1'], ['sat_1', 'sat_2']]

        timezone = pytz.timezone("UTC")
        start_time = timezone.localize(datetime(2018, 1, 1, 10, 0, 0))

        interval_start_time, visible_sats = self.scheduler.find_max_visible_satellites_interval_non_cumulative(
            [None], None, start_time, 120, 60)
        self.assertTrue(interval_start_time.utc_datetime() == start_time + timedelta(hours=1))
        self.assertTrue(visible_sats == ['sat_1', 'sat_2'])

    @patch.object(Scheduler, "find_visible_satellites_instance")
    def test_find_max_visible_satellites_interval_cumulative(self, mock_find_visible_satellites_instance):
        mock_find_visible_satellites_instance.side_effect = [['sat_1', 'sat_2'], ['sat_2', 'sat_3']]

        timezone = pytz.timezone("UTC")
        start_time = timezone.localize(datetime(2018, 1, 1, 10, 0, 0))

        interval_start_time, visible_sats = self.scheduler.find_max_visible_satellites_interval_cumulative(
            [None], None, start_time, 120, 60)
        self.assertTrue(interval_start_time.utc_datetime() == start_time)
        self.assertTrue(len(visible_sats) == 3)


if __name__ == "__main__":
    unittest.main()
