from flask import Flask, current_app
from flask.ext.sqlalchemy import SQLAlchemy
import os
from rq import Queue
from rq.job import Job

from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
q = Queue(connection=conn)