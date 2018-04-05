To devlop locally, use (copy-pasting line by line might still be safer)  
$ source setup.sh

It'll
- install dependencies (postgresql, redis-server, python3 and pip3)
- install virtualenv and virtualenvwrapper with some required environment variables
- create a virtualenv for the app with environment variables
- install python modules
- setup the postgres database

Once setup, activate the virtual environment  
$ workon lbcalert  
start the redis server  
$ redis-server  
start a worker  
$ python3 worker.py  
launch the app  
$ python3 main.py  
