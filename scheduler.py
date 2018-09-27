from skyfield.api import Loader
import datetime, time
from datetime import datetime

class IllegalArgumentException(Exception):
    pass

class Scheduler:
    def __init__(self):
        self._skyload = Loader('~/.skyfield-data')
        self.ts = self._skyload.timescale()


    def find_time(self, satlist_url='http://celestrak.com/NORAD/elements/visual.txt',
    start_time=datetime.now(), n_windows=24, duration=60, sample_interval=1, cumulative=False):
        '''arguments: satlist_url (string) a URL to a file containing a list of Earth-orbiting
        satellites in TLE format)
                      start_time: a Python Datetime object representing the
                      the start of the potential observation windows,return

                      duration: the size (in minutes) of an observation window - must be positive
                      n_windows: the number of observation windows to check.  Must be a positive integer
                      sample_interval: the interval (in minutes) at which the visible
                      satellites are checked.  Must be smaller than duration.
                      cumulative: a boolean to determine whether we look for the maximum number
                      of satellites visible at any time within the duration (if False), or the
                      cumulative number of distinct satellites visible over the duration (if True)

        returns:a tuple ( interval_start_time, satellite_list), where start_interval is
        the time interval from the set {(start_time, start_time + duration),
        (start_time + duration, start_time + 2*duration)...} where either the
        most satellites are visible at any one time (as checked at every interval)
        minutes, or cumulatively the most unique satellites are visible over the duration (as unchecked
        every interval minutes), and satellite_list is a list of strings containing the
        names of satellites that contribute to the total/
        raises: IllegalArgumentException if an illegal argument is provided'''
        return (start_time, ["ISS (ZARYA)", "COSMOS-123"])
