from app import app, db
import models
import parser
from scheduler import Scheduler, task
import router

scheduler = Scheduler(60, task)
scheduler.start()