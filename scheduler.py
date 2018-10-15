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

        observer_location = Topos(location[0], location[1])

        # a list of Satellite objects
        satellites_list = self.get_all_satellites(satlist_url)

        start_time_max_sub_interval, visible_satellites_max_sub_interval = self.find_max_visible_satellites_interval_non_cumulative(satellites_list, observer_location,
                                                                                                                                    start_time, duration, sample_interval)

        print('There are at maximum ', len(visible_satellites_max_sub_interval), 'visible satellites')
        for visible_satellite in visible_satellites_max_sub_interval:
            print(visible_satellite.name)

        print('the start time is ', start_time_max_sub_interval)

        #return (start_time, ["ISS (ZARYA)", "COSMOS-123"])

    def get_all_satellites(self, satellite_list_url='http://celestrak.com/NORAD/elements/visual.txt'):

        try:
            satellites = load.tle(satellite_list_url)
        except Exception as e:
            print(e)
            raise IllegalArgumentException

        satellites_list = []

        for satellite in satellites:

            satellite_name = satellite
            satellite_info = satellites[satellite_name]

            current_satellite = Satellite(satellite_name, satellite_info)

            satellites_list.append(current_satellite)

        return satellites_list

    def find_visible_satellites_instance(self, satellites_list, observer_location, time_of_measurement):

        # if the satellites list is empty then we return an empty array
        visible_satellites = []

        # NOT SURE IF WE NEED TO TYPE CHECK EACH ELEMENT IN THE ARRAY TO SEE IF THEY ARE SATELLITE OBJECTS OR NOT

        for satellite in satellites_list:

            satellite_altitude = satellite.get_altitude(observer_location, time_of_measurement)
            satellite_elevation = satellite_altitude.degrees

            if satellite.is_visible(satellite_elevation):
                visible_satellites.append(satellite)

        return visible_satellites

    def find_max_visible_satellites_interval_non_cumulative(self, satellites_list, observer_location, start_time, interval_duration, sub_interval_duration):

        if not satellites_list:
            return None, []

        for satellite in satellites_list:
            if type(satellite) is not Satellite:
                raise IllegalArgumentException

        max_number_of_visible_satellites_sub_interval = 0

        start_time_of_max_sub_interval = self.ts.utc(start_time)

        number_of_sub_intervals = interval_duration // sub_interval_duration

        visible_satellites_max_sub_interval = []

        for sub_interval in range(number_of_sub_intervals):

            time_of_measurement = self.ts.utc(start_time + timedelta(minutes=sub_interval * sub_interval_duration))

            visible_satellites_sub_interval = self.find_visible_satellites_instance(satellites_list, observer_location,
                                                                                    time_of_measurement)

            number_of_visible_satellites_sub_interval = len(visible_satellites_sub_interval)

            if max_number_of_visible_satellites_sub_interval < number_of_visible_satellites_sub_interval:
                max_number_of_visible_satellites_sub_interval = number_of_visible_satellites_sub_interval
                start_time_of_max_sub_interval = time_of_measurement
                visible_satellites_max_sub_interval = visible_satellites_sub_interval

        return start_time_of_max_sub_interval, visible_satellites_max_sub_interval


class Satellite:

    def __init__(self, name, info):

        self.name = name
        self.info = info

    def get_altitude(self, observer_location, time_of_measurement):

        location_difference = self.info - observer_location
        location_difference = location_difference.at(time_of_measurement)

        altitude, azimuth, distance = location_difference.altaz()

        return altitude

    def is_visible(self, position_elevation):

        result = False

        if position_elevation > 0:
            result = True

        return result


a = Scheduler()
a.find_time()