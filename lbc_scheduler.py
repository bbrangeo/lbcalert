import logging
LOGGER = logging.getLogger('lbcalert').getChild('scheduler')

from scheduler import Scheduler
from models import Search
from lbcparser import parselbc

# TODO mutexes to protect database
# TODO move proxymanager here to maintain proxy list

def task():
    LOGGER.info("[scheduler] start task")
    ids = [search.id for search in Search.query.all()]
    for id in ids:
        parselbc(id)
    LOGGER.info("[scheduler] end task")

scheduler = Scheduler(300, task)
scheduler.start()

if __name__ == "__main__":
    task()
