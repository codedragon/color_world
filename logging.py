from datetime import datetime
from time import mktime


def micro_time():
    """
    Returns the current time since epoch, accurate to the
    value returned by gettimeofday(), usually ~1microsecond.
    Datetime is more accurate than time.clock
    """
    now = datetime.now()
    return long(mktime(now.timetuple()) * 1000000 + now.microsecond)


class Logging(object):
    def __init__(self):
        self.filename = 'color_' + datetime.now().strftime("%Y_%m_%d_%H_%M")
        self.log_file = self.start_logging()

    def start_logging(self):
        log_file = open(self.filename, 'a')
        return log_file

    def write_line(self, *args):
        self.log_file.write(str(micro_time()) + ' {} yup\n'.format(args))

    def stop_logging(self):
        self.log_file.close()