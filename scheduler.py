from threading import Timer, Thread
from time import sleep

from app import q
from models import Search, LBCentry
from parser import parselbc

class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None

def task():
    refresh_searches()

def refresh_searches():
    searches = Search.query.all()
    for search in searches:
        q.enqueue_call(
            func=parselbc, args=(search.id,)
        )

scheduler = Scheduler(300, task)
scheduler.start()