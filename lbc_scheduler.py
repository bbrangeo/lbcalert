from scheduler import Scheduler
from models import Search
from lbcparser import parselbc

import logging

logger = logging.getLogger().getChild('scheduler')
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

# TODO mutexes to protect database
# TODO move proxymanager here to maintain proxy list

def task():
    logger.info("[scheduler] start task")
    ids = [search.id for search in Search.query.all()]
    for id in ids:
        parselbc(id)
    logger.info("[scheduler] end task")

scheduler = Scheduler(300, task)
scheduler.start()