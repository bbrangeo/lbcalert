import logging
if __name__ == "__main__":
    logging.getLogger('lbcalert').setLevel(logging.INFO)
    logging.getLogger('lbcalert').addHandler(logging.StreamHandler())
LOGGER = logging.getLogger('lbcalert').getChild('proxy')

import requests

from scheduler import Scheduler
from proxy_manager.manager import ProxyManager

lbc_proxy_manager = ProxyManager.\
                        import_proxy_manager(export_files={
                                                'good_proxies':'proxy_manager/good_proxies',
                                                'bad_proxies':'proxy_manager/bad_proxies',
                                                'banned_proxies':'proxy_manager/banned_proxies'
                                             })

def update_proxies():
    LOGGER.info("[lbc_proxies] unbanning proxies")
    lbc_proxy_manager.unban_oldest(24)
    LOGGER.info("[lbc_proxies] updating proxies")
    lbc_proxy_manager.fetch_sources()
    LOGGER.info("[lbc_proxies] %d (assumed) good proxies in manager",
                lbc_proxy_manager.good_proxy_count())
    LOGGER.info("[lbc_proxies] exporting proxies")
    lbc_proxy_manager.export_proxy_manager()
    return

proxy_scheduler = Scheduler(update_proxies, 3600)
proxy_scheduler.start()

if __name__ == "__main__":
    update_proxies()