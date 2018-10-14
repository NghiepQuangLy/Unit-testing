'''A class to calculate optimal times for satellite spotting
Initial skeleton code written by Robert Merkel for FIT2107 Assignment 3
'''

from skyfield.api import Loader, Topos, load
import datetime, time
from datetime import datetime, timedelta
import pytz

class IllegalArgumentException(Exception):
    '''An exception to throw if somebody provides invalid data to the Scheduler methods'''
    pass

class Scheduler:
    '''The class for calculating optimal satellite spotting times.  You can and should add methods
    to this, but please don't change the parameter list for the existing methods.  '''
    def __init__(self):
        '''Constructor sets things to put downloaded data in a sensible location. You can add
        to this if you want.  '''
        self._skyload = Loader('~/.skyfield-data')
        self.ts = self._skyload.timescale()


    def find_time(self, satlist_url='http://celestrak.com/NORAD/elements/visual.txt',
    start_time=datetime.now(), n_windows=24, duration=60, sample_interval=1, cumulative=False,
    location=(-37.910496,145.134021)):
        '''NOTE: this is the key function that you'll need to implement for the assignment.  Please
        don't change the arguments.
        arguments: satlist_url (string) a URL to a file containing a list of Earth-orbiting
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
                      location: a tuple (lat, lon) of floats specifying he latitude and longitude of the
                      observer.  Negative latitudes specify the southern hemisphere, negative longitudes
                      the western hemisphere.  lat must be in the range [-90,90], lon must be in the
                      range [-180, 180]
        returns:a tuple ( interval_start_time, satellite_list), where start_interval is
        the time interval from the set {(start_time, start_time + duration),
        (start_time + duration, start_time + 2*duration)...} with the most satellites visible at some
        point in the interval, or the most cumulative satellites visible over the interval (if cumulative=True)
        See the assignment spec sheet for more details.
        raises: IllegalArgumentException if an illegal argument is provided'''

        """
        Dealing with naive start_time which is a datetime object with no timezone
        """
        timezone = pytz.timezone("UTC")
        start_time = timezone.localize(start_time)
        """
        """

        assert ((start_time.tzinfo is not None) and (str (start_time.tzinfo) == "UTC")), "Start time must be UTC time"
        assert (type(duration) is int), "Duration must be an integer"
        assert (type(n_windows) is int), "The number of observation windows must be an integer"
        assert (type(sample_interval) is int), "The sample interval must be an integer"
        assert (type(location[0]) is int or type(location[0]) is float), "Latitude has incorrect data type"
        assert (type(location[1]) is int or type(location[1]) is float), "Longitude has incorrect data type"
        assert (type(cumulative) is bool), "Cumulative needs to be either True or False"

        assert (0 < duration), "Duration in minutes must be positive"
        assert (0 < n_windows), "The number of observation windows must be a positive integer"
        assert (0 < sample_interval < duration), "The sample interval must be positive and is smaller than the duration"
        assert (-90 <= location[0] <= 90), "Latitude must be between -90 and 90"
        assert (-180 <= location[1] <= 180), "Longitude must be between -180 and 180"

        try:
            satellites = load.tle(satlist_url)
        except Exception as e:
            print(e)
            return

        timescale = load.timescale()
        start_time = timescale.utc(start_time)

        observer_location = Topos(location[0], location[1])

        for satellite in satellites:

            satellite_name = satellite
            satellite_info = satellites[satellite_name]

            current_satellite = Satellite(satellite_name, satellite_info)

            current_satellite_altitude = current_satellite.get_altitude(observer_location, start_time)
            current_satellite_elevation = current_satellite_altitude.degrees

            if current_satellite.is_visible(current_satellite_elevation):
                print(current_satellite.name)

        #https://rhodesmill.org/skyfield/earth-satellites.html  LOOK AT THIS FOR POSITION

        #return (start_time, ["ISS (ZARYA)", "COSMOS-123"])

class Satellite:

    def __init__(self, name, info):

        self.name = name
        self.info = info

    def get_altitude(self, observer_location, current_time):

        location_difference = self.info - observer_location
        location_difference = location_difference.at(current_time)

        altitude, azimuth, distance = location_difference.altaz()

        return altitude

    def is_visible(self, position_elevation):

        result = False

        if position_elevation > 0:
            result = True

        return result


a = Scheduler()
a.find_time()