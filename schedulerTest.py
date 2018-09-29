import unittest
from scheduler import Scheduler
from scheduler import IllegalArgumentException
from datetime import datetime
class SchedulerTest(unittest.TestCase):
    '''Tests for the scheduler class.  Add more tests
    to test the code that you write'''

    def setUp(self):
        self.scheduler = Scheduler()

    def test_itsalive(self):
        (stime, satellites) = self.scheduler.find_time()
        self.assertTrue(type(stime)==type(datetime.now()))
        self.assertTrue(satellites[0]=="ISS (ZARYA)")
        self.assertTrue(satellites[1]=="COSMOS-123")

    def test_exceptionthrown(self):
        with self.assertRaises(IllegalArgumentException):
            (stime, satellites) = self.scheduler.find_time(start_time = "now")

if __name__=="__main__":
    unittest.main()
