#!/bin/bash

## to be run with "source"

# redis is the "mini-db" used to store the parse queue
sudo add-apt-repository ppa:chris-lea/redis-server

# system-wide required packages
sudo apt-get update
sudo apt-get install build-essential postgresql postgresql-contrib redis-server
sudo apt-get install libpq-dev python3-dev python3-pip

# launch the db server
sudo service postgresql start

# install virtualenv and wrapper to manage python virtualenvs
sudo pip3 install --upgrade virtualenv
sudo pip3 install --upgrade virtualenvwrapper

# add environment variables to bashrc (part of virtualenvwrapper install) 
echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
echo 'export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc

# activate these env variables
source ~/.bashrc

# create the virtualenv for our app with its own env variables
mkvirtualenv -p python3 ~/.virtualenvs/lbcalert
echo 'export APP_SETTINGS="config.DevelopmentConfig"' >> ~/.virtualenvs/lbcalert/bin/postactivate
echo 'export DATABASE_URL="postgresql:///lbcalert_dev"' >>  ~/.virtualenvs/lbcalert/bin/postactivate
echo 'export FLASK_APP=main.py' >> ~/.virtualenvs/lbcalert/bin/postactivate
echo 'export MAIL_USERNAME=lbcbot@gmail.com' >> ~/.virtualenvs/lbcalert/bin/postactivate
echo 'export MAIL_PASSWORD=wwyxbctykwlctafx' >> ~/.virtualenvs/lbcalert/bin/postactivate

# activate the virtualenv
workon lbcalert

# setup app-specific python modules
pip install -r requirements.txt

# psql role and db creation
sudo su - postgres <<WRAP
createuser -d $USER
psql -c 'alter user $USER with createdb'
WRAP
createdb -E UTF8 -T template0 lbcalert_dev

# update db from migration files
flask db upgrade
