import logging
if __name__ == "__main__":
    logging.getLogger('lbcalert').setLevel(logging.INFO)
    logging.getLogger('lbcalert').addHandler(logging.StreamHandler())
LOGGER = logging.getLogger('lbcalert').getChild('search_scheduler')

from scheduler import Scheduler
from models import Search
from parser import parselbc

# TODO mutexes to protect database
# TODO move proxymanager here to maintain proxy list

def run_searches():
    LOGGER.info("[search_scheduler] start task")
    search_ids = [search.id for search in Search.query.all()]
    for search_id in search_ids:
        parselbc(search_id)
    LOGGER.info("[search_scheduler] end task")

# randomize from 2.5 to 5 minutes
search_scheduler = Scheduler(run_searches, 300, 0.5)
search_scheduler.start()

if __name__ == "__main__":
    run_searches()