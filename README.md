DEPRECATED

## LBCalert

An alert system for a familiar classifieds service

Initial code based on [Flask by Example Tutorial](https://realpython.com/flask-by-example-part-1-project-setup)

#### Local development

To devlop locally, use (copy-pasting line by line might still be safer)  
$ source setup.sh

It'll
- install dependencies (postgresql, redis-server, python3 and pip3)
- create a virtualenv for the app with environment variables
- install python modules
- setup the postgres database

Once setup, activate the virtual environment  
$ source .venv/bin/activate
start the redis server  
$ redis-server  
start a worker  
$ python worker.py  
launch the app  
$ python main.py  
