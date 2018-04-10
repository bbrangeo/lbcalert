from worker import conn
from scheduler import Scheduler
from rq import Connection, get_failed_queue
from models import Search
from lbcparser import parselbc

from app import q

# TODO launch as separate service ?
def task():
    # Clear failed jobs
    with Connection(conn):
        fq = get_failed_queue()
    for job in fq.jobs:
            print("delete job " + job.id)
            job.delete()
    searches = Search.query.all()
    for search in searches:
        job = q.enqueue_call(
            func=parselbc, args=(search.id,1), result_ttl=0
        )
        print(search.title)

scheduler = Scheduler(600, task)
scheduler.start()