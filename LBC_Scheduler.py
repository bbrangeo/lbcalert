from scheduler import Scheduler
from models import Search
from lbcparser import parselbc

from app import q

# TODO launch as separate service ?
def task():
    q.failed_job_registry.cleanup()
    searches = Search.query.all()
    for search in searches:
        job = q.enqueue_call(
            func=parselbc, args=(search.id,1), result_ttl=0
        )
        print(search.title)

scheduler = Scheduler(300, task)
scheduler.start()
