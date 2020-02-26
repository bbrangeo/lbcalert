import logging
lbcalert_logger = logging.getLogger('lbcalert')
lbcalert_logger.setLevel(logging.INFO)
lbcalert_handler = logging.StreamHandler()
# lbcalert_formatter = logging.Formatter('%(threadName)s %(message)s')
# lbcalert_handler.setFormatter(lbcalert_formatter)
lbcalert_logger.addHandler(lbcalert_handler)

# impose import order
from app import app, db
import models
import login
import search_scheduler
import proxy_scheduler
import router

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
