'''A class to calculate optimal times for satellite spotting
Initial skeleton code written by Robert Merkel for FIT2107 Assignment 3
'''

from skyfield.api import Topos, load
import datetime, time
from datetime import datetime, timedelta
from datetime import timezone as dttz
from pytz import timezone

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
    start_time=datetime.now(), n_windows=24, duration=60, sample_interval=1, cumulative=False):
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

        returns:a tuple ( interval_start_time, satellite_list), where start_interval is
        the time interval from the set {(start_time, start_time + duration),
        (start_time + duration, start_time + 2*duration)...} with the most satellites visible at some
        point in the interval, or the most cumulative satellites visible over the interval (if cumulative=True)
        See the assignment spec sheet for more details.
        raises: IllegalArgumentException if an illegal argument is provided'''
        return (start_time, ["ISS (ZARYA)", "COSMOS-123"])

def convert_coords(lat,lon):
    lat_float = float(lat)
    lon_float = float(lon)

    if lat_float > 0:
        lat_char = ' N'
    else:
        lat_char = ' S'

    if lon_float > 0:
        lon_char = ' E'
    else:
        lon_char = ' W'

    return (str(abs(lat_float)) + lat_char, str(abs(lon_float)) + lon_char)

def get_alt(satellite, time , lat, lon):
    coords_NESW = convert_coords(lat, lon)
    location = Topos(coords_NESW[0], coords_NESW[1])
    difference = satellite - location
    ts = load.timescale()
    t = ts.utc(time.astimezone(timezone('UTC')))
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()

    return alt

def is_visible(satellite, time, lat, lon):
    alt = get_alt(satellite, time , lat, lon).signed_dms()[0]
    if alt > 0:
        return True
    else:
        return False

def utc_to_local(t_utc):
    t_local = t_utc.replace(tzinfo=dttz.utc).astimezone(tz=None)
    return t_local

def local_to_utc(t_local):
    t_utc = t_local.astimezone(timezone('UTC'))
    return t_utc

stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
satellites = load.tle(stations_url)
satellite = satellites['ISS (ZARYA)']
t = datetime.now()
a = 2

ts = load.timescale()
utc_t = ts.utc(t.astimezone(timezone('UTC')))

NESW = convert_coords(-37.910496, 145.134021)


def get_max_sat(start, duration, inter, sat_list ,lat,lon):
    sat_obv = [None]*(duration//inter)
    for j in range(len(sat_obv)):
        sat_obv[j] = 0
    for i in range(len(sat_obv)):
        for k,sat in sat_list.items():
            if is_visible(sat,start+timedelta(minutes=inter*i),lat,lon):
                sat_obv[i] += 1
                print(sat)
    return max(sat_obv)

print(get_max_sat(local_to_utc(datetime.now()),3,1,satellites,-37.910496,145.134021))

