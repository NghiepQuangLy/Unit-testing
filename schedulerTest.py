import unittest
from scheduler import Scheduler
from scheduler import Satellite
from scheduler import IllegalArgumentException
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
import pytz


naive_testing_time = datetime.now()
timezone = pytz.timezone("UTC")
non_naive_testing_time = timezone.localize(naive_testing_time)


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

class TestingSatellite:
    """ Class to allow for `.name` in testing. """

    def __init__(self, name):
        self.name = name

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

    @patch("skyfield.api.load.tle", return_value={'sat_1': TestingSatellite('sat_1'),
                                                  'sat_2': TestingSatellite('sat_2'),
                                                  'sat_3': TestingSatellite('sat_3'),
                                                  'sat_4': TestingSatellite('sat_2')})
    def test_get_all_satellites(self, mock_skyfield_load_tle):

        satellites_url = MagicMock()

        satellites_list = self.scheduler.get_all_satellites(satellites_url)

        self.assertTrue(satellites_list[0].name == 'sat_1')
        self.assertTrue(satellites_list[1].name == 'sat_2')
        self.assertTrue(satellites_list[2].name == 'sat_3')

    @patch.object(Scheduler, "find_max_visible_satellites_interval_cumulative")
    def test_find_time_cumulative_naive_time(self, mock_find_max_visible_satellites_interval_cumulative):

        global naive_testing_time
        global non_naive_testing_time

        mock_values = [[non_naive_testing_time + timedelta(hours=0), [Satellite('sat_1',  None),
                                                                      Satellite('sat_2',  None)]],
                       [non_naive_testing_time + timedelta(hours=1), [Satellite('sat_1',  None),
                                                                      Satellite('sat_2',  None),
                                                                      Satellite('sat_3',  None)]],
                       [non_naive_testing_time + timedelta(hours=2), [Satellite('sat_1',  None),
                                                                      Satellite('sat_4',  None),
                                                                      Satellite('sat_7',  None),
                                                                      Satellite('sat_10', None)]],
                       [non_naive_testing_time + timedelta(hours=3), []]]
        mock_find_max_visible_satellites_interval_cumulative.side_effect = mock_values

        max_interval_start, max_interval_satellites = self.scheduler.find_time(start_time=naive_testing_time,
                                                                               n_windows=4, cumulative=True)

        self.assertTrue(self.check_times_equal(max_interval_start, non_naive_testing_time + timedelta(hours=2)))
        self.assertTrue(max_interval_satellites == ['sat_1', 'sat_4', 'sat_7', 'sat_10'])

    @patch.object(Scheduler, "find_max_visible_satellites_interval_cumulative")
    def test_find_time_cumulative_non_naive_time(self, mock_find_max_visible_satellites_interval_cumulative):

        global non_naive_testing_time

        mock_values = [[non_naive_testing_time + timedelta(hours=0), [Satellite('sat_1',  None),
                                                                      Satellite('sat_2',  None)]],
                       [non_naive_testing_time + timedelta(hours=1), [Satellite('sat_1',  None),
                                                                      Satellite('sat_2',  None),
                                                                      Satellite('sat_3',  None)]],
                       [non_naive_testing_time + timedelta(hours=2), [Satellite('sat_1',  None),
                                                                      Satellite('sat_4',  None),
                                                                      Satellite('sat_7',  None),
                                                                      Satellite('sat_10', None)]],
                       [non_naive_testing_time + timedelta(hours=3), []]]
        mock_find_max_visible_satellites_interval_cumulative.side_effect = mock_values

        max_interval_start, max_interval_satellites = self.scheduler.find_time(start_time=non_naive_testing_time,
                                                                               n_windows=4, cumulative=True)

        self.assertTrue(self.check_times_equal(max_interval_start, non_naive_testing_time + timedelta(hours=2)))
        self.assertTrue(max_interval_satellites == ['sat_1', 'sat_4', 'sat_7', 'sat_10'])

    @patch.object(Scheduler, "find_max_visible_satellites_interval_cumulative")
    def test_find_time_non_cumulative(self, mock_find_max_visible_satellites_interval_non_cumulative):

        global non_naive_testing_time

        mock_values = [[non_naive_testing_time + timedelta(hours=0), [Satellite('sat_1',  None),
                                                                      Satellite('sat_2',  None)]],
                       [non_naive_testing_time + timedelta(hours=1), [Satellite('sat_1',  None),
                                                                      Satellite('sat_2',  None),
                                                                      Satellite('sat_3',  None)]],
                       [non_naive_testing_time + timedelta(hours=2), [Satellite('sat_1',  None),
                                                                      Satellite('sat_4',  None),
                                                                      Satellite('sat_7',  None),
                                                                      Satellite('sat_10', None)]],
                       [non_naive_testing_time + timedelta(hours=3), []]]
        mock_find_max_visible_satellites_interval_non_cumulative.side_effect = mock_values

        max_interval_start, max_interval_satellites = self.scheduler.find_time(start_time=non_naive_testing_time,
                                                                               n_windows=4, cumulative=True)

        self.assertTrue(self.check_times_equal(max_interval_start, non_naive_testing_time + timedelta(hours=2)))
        self.assertTrue(max_interval_satellites == ['sat_1', 'sat_4', 'sat_7', 'sat_10'])

    def test_find_visible_satellites_instance_non_satellite(self):
        with self.assertRaises(IllegalArgumentException):
            satellites_list = [Satellite('sat_1', None),
                               Satellite('sat_2', None),
                               'a',
                               Satellite('sat_4', None)]

            self.scheduler.find_visible_satellites_instance(satellites_list, None, None)

    @patch.object(Satellite, "get_altitude")
    def test_find_visible_satellites_instance(self, mock_get_altitude):

        satellites_list = [Satellite('sat_1', None),
                           Satellite('sat_2', None),
                           Satellite('sat_3', None),
                           Satellite('sat_4', None)]

        mock_values = [TestingAlt(10),
                       TestingAlt(-10),
                       TestingAlt(-10),
                       TestingAlt(10)]
        mock_get_altitude.side_effect = mock_values

        visible_satellites = self.scheduler.find_visible_satellites_instance(satellites_list, None, None)

        self.assertTrue([visible_satellites[0].name == 'sat_1'])
        self.assertTrue([visible_satellites[1].name == 'sat_4'])

    def test_find_max_visible_satellites_interval_non_cumulative_empty_satellites(self):

        global non_naive_testing_time

        interval_start_time, visible_satellites = self.scheduler.find_max_visible_satellites_interval_non_cumulative(
            [], None, non_naive_testing_time, 120, 30)

        self.assertTrue(interval_start_time is None)
        self.assertTrue(visible_satellites == [])

    def test_find_max_visible_satellites_interval_non_cumulative_interval_duration_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_non_cumulative(
                [None], None, non_naive_testing_time, 'a', 30)

    def test_find_max_visible_satellites_interval_non_cumulative_sub_interval_duration_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_non_cumulative(
                [None], None, non_naive_testing_time, 120, 'a')

    def test_find_max_visible_satellites_interval_non_cumulative_interval_duration_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_non_cumulative(
                [None], None, non_naive_testing_time, 0, 30)

    def test_find_max_visible_satellites_interval_non_cumulative_sub_interval_duration_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_non_cumulative(
                [None], None, non_naive_testing_time, 120, 0)

    @patch.object(Scheduler, "find_visible_satellites_instance")
    def test_find_max_visible_satellites_interval_non_cumulative(self, mock_find_visible_satellites_instance):

        global non_naive_testing_time

        mock_values = [['sat_1'],
                       ['sat_1', 'sat_2'],
                       ['sat_2', 'sat_3'],
                       ['sat_4']]
        mock_find_visible_satellites_instance.side_effect = mock_values

        interval_start_time, visible_satellites = self.scheduler.find_max_visible_satellites_interval_non_cumulative(
            [None], None, non_naive_testing_time, 120, 30)

        self.assertTrue(self.check_times_equal(interval_start_time.utc_datetime(),
                                               non_naive_testing_time + timedelta(minutes=30)))
        self.assertTrue(visible_satellites == ['sat_1', 'sat_2'])

    def test_find_max_visible_satellites_interval_cumulative_empty_satellites(self):

        global non_naive_testing_time

        interval_start_time, visible_satellites = self.scheduler.find_max_visible_satellites_interval_cumulative(
            [], None, non_naive_testing_time, 120, 30)

        self.assertTrue(interval_start_time is None)
        self.assertTrue(visible_satellites == [])

    def test_find_max_visible_satellites_interval_cumulative_interval_duration_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_cumulative(
                [None], None, non_naive_testing_time, 'a', 30)

    def test_find_max_visible_satellites_interval_cumulative_sub_interval_duration_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_cumulative(
                [None], None, non_naive_testing_time, 120, 'a')

    def test_find_max_visible_satellites_interval_cumulative_interval_duration_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_cumulative(
                [None], None, non_naive_testing_time, 0, 30)

    def test_find_max_visible_satellites_interval_cumulative_sub_interval_duration_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            global non_naive_testing_time

            self.scheduler.find_max_visible_satellites_interval_cumulative(
                [None], None, non_naive_testing_time, 120, 0)

    @patch.object(Scheduler, "find_visible_satellites_instance")
    def test_find_max_visible_satellites_interval_cumulative(self, mock_find_visible_satellites_instance):

        global non_naive_testing_time

        mock_values = [['sat_1'],
                       ['sat_1', 'sat_2'],
                       ['sat_2', 'sat_3'],
                       ['sat_4']]
        mock_find_visible_satellites_instance.side_effect = mock_values

        interval_start_time, visible_satellites = self.scheduler.find_max_visible_satellites_interval_cumulative(
            [None], None, non_naive_testing_time, 120, 30)

        visible_satellites.sort()

        self.assertTrue(self.check_times_equal(interval_start_time.utc_datetime(), non_naive_testing_time))
        self.assertTrue(visible_satellites == ['sat_1', 'sat_2', 'sat_3', 'sat_4'])


if __name__ == "__main__":
    unittest.main()
