from scheduler import Scheduler
from models import Search
from lbcparser import parselbc

from rq import Queue
from worker import conn

q = Queue(connection=conn)

# TODO launch as separate service ?
def task():
    q.failed_job_registry.cleanup()
    searches = Search.query.all()
    for search in searches:
        job = q.enqueue(
            parselbc, search.id, result_ttl=0
        )
        print(search.title)

scheduler = Scheduler(300, task)
scheduler.start()