# impose import order
from app import app, db
import models
import login
import lbc_scheduler
import router

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
