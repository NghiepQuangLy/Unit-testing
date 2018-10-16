import unittest
from scheduler import Scheduler
from scheduler import Satellite
from scheduler import IllegalArgumentException
from datetime import datetime

#
# class SatelliteTest(unittest.TestCase):
#
#     def setUp(self):
#         self.satellite = Satellite()

class SchedulerTest(unittest.TestCase):
    '''Tests for the scheduler class.  Add more tests
    to test the code that you write'''

    def setUp(self):
        self.scheduler = Scheduler()

    def test_its_alive(self):
        (stime, satellites) = self.scheduler.find_time()
        self.assertTrue(type(stime)==type(datetime.now()))
        # self.assertTrue(satellites[0]=="ISS (ZARYA)")
        # self.assertTrue(satellites[1]=="COSMOS-123")

    def test_find_time_start_time_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(start_time = "now")

    def test_find_time_duration_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(duration = 'a')

    def test_find_time_duration_non_positive(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(duration = -1)

    def test_find_time_n_windows_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(n_windows = 'a')

    def test_find_time_n_windows_non_positive(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(n_windows = 0)

    def test_find_time_sample_interval_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(sample_interval = 'a')

    def test_find_time_sample_interval_non_positive(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(sample_interval = 0)

    def test_find_time_sample_interval_bigger_than_duration(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(sample_interval = 70, duration = 60)

    def test_find_time_location_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location = 'a')

    def test_find_time_location_invalid_list_or_tuple(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location = (1, 2, 3))

    def test_find_time_location_latitude_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location = ('a', 0))

    def test_find_time_location_latitude_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location = (-100, 0))

    def test_find_time_location_longitude_wrong_type(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location = (0, 'a'))

    def test_find_time_location_longitude_out_of_range(self):
        with self.assertRaises(IllegalArgumentException):
            self.scheduler.find_time(location = (0, 200))

if __name__=="__main__":
    unittest.main()
