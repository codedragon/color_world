import datetime
import time


def micro_time():
    """
    Returns the current time since epoch, accurate to the
    value returned by gettimeofday(), usually ~1microsecond.
    Datetime is more accurate than time.clock
    """
    now = datetime.datetime.now()
    return long(time.mktime(now.timetuple()) * 1000000 + now.microsecond)


