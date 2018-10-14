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

        timescale = load.timescale()

        observer_location = Topos(location[0], location[1])

        # a list of Satellite objects
        satellites_list = self.get_all_satellites(satlist_url)

        visible_satellites_interval = self.find_visible_satellites_interval(timescale, satellites_list,
                                                                            observer_location, start_time, duration,
                                                                            sample_interval)

        max_visible_satellites = self.find_max_number_visible_satellites_interval(visible_satellites_interval)

        print('There are at maximum ', len(max_visible_satellites), 'visible satellites')
        for vis_sat in max_visible_satellites:
            print(vis_sat.name)
        
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

        visible_satellites = []

        for satellite in satellites_list:

            satellite_altitude = satellite.get_altitude(observer_location, time_of_measurement)
            satellite_elevation = satellite_altitude.degrees

            if satellite.is_visible(satellite_elevation):
                visible_satellites.append(satellite)

        return visible_satellites


    def find_visible_satellites_interval(self, timescale, satellites_list, observer_location, start_time, interval_duration, sub_interval_duration):

        number_of_sub_intervals = interval_duration // sub_interval_duration

        visible_satellites_interval = [None] * number_of_sub_intervals

        for sub_interval in range(number_of_sub_intervals):

            time_of_measurement = timescale.utc(start_time + timedelta(minutes=sub_interval * sub_interval_duration))

            visible_satellites_sub_interval = self.find_visible_satellites_instance(satellites_list, observer_location,
                                                                                    time_of_measurement)

            visible_satellites_interval[sub_interval] = visible_satellites_sub_interval

        return visible_satellites_interval

    def find_max_number_visible_satellites_interval(self, visible_satellites_interval):

        # checking if visible_satellites_interval actually contains data or not; if not we just return empty array
        if visible_satellites_interval:
            max_number = 0
            max_sub_interval = None
            number_of_sub_intervals = len(visible_satellites_interval)

            for sub_interval in range(number_of_sub_intervals):

                number_of_visible_satellites_sub_interval = len(visible_satellites_interval[sub_interval])

                if max_number < number_of_visible_satellites_sub_interval:
                    max_number = number_of_visible_satellites_sub_interval
                    max_sub_interval = sub_interval

            return visible_satellites_interval[max_sub_interval]
        return []


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