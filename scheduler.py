from threading import Timer
from time import sleep
import random
import logging
LOGGER = logging.getLogger('lbcalert').getChild('scheduler')

class Scheduler(object):
    def __init__(self, function, max_sleep_time, randomize=0):
        self.max_sleep_time = max_sleep_time
        self.randomize = randomize
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.get_sleep_time(), self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def get_sleep_time(self):
        if self.randomize>0:
            sleep_time = int((1-random.uniform(0, self.randomize))*self.max_sleep_time)
        else:
            sleep_time = self.max_sleep_time
        LOGGER.info("[scheduler] sleep time : %d seconds" % sleep_time)
        return sleep_time

    def _run(self):
        self.function()
        self._t = Timer(self.get_sleep_time(), self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None