from app import app, db
import models
from parser import task
import router
from scheduler import Scheduler

scheduler = Scheduler(60, task)
scheduler.start()

if __name__=="__main__":
    app.run(host="0.0.0.0")