import logging
if __name__ == "__main__":
    logging.getLogger('lbcalert').setLevel(logging.INFO)
    logging.getLogger('lbcalert').addHandler(logging.StreamHandler())
LOGGER = logging.getLogger('lbcalert').getChild('lbc_scheduler')

from scheduler import Scheduler
from models import Search
from lbcparser import parselbc, lbc_proxy_manager

# TODO mutexes to protect database
# TODO move proxymanager here to maintain proxy list

def task():
    lbc_proxy_manager.unban_oldest(24)
    LOGGER.info("[scheduler] start task")
    LOGGER.info("[scheduler] %d (assumed) good proxies in manager",
                lbc_proxy_manager.good_proxy_count())
    ids = [search.id for search in Search.query.all()]
    for id in ids:
        parselbc(id)
    LOGGER.info("[scheduler] backing up proxies")
    lbc_proxy_manager.export_proxy_manager()
    LOGGER.info("[scheduler] end task")

scheduler = Scheduler(300, task)
scheduler.start()

if __name__ == "__main__":
    task()