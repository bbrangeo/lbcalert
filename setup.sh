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

# create the virtualenv for our app with its own env variables
python -m venv .venv
echo 'export APP_SETTINGS="config.DevelopmentConfig"' >> .venv/bin/activate
echo 'export DATABASE_URL="postgresql:///lbcalert_dev"' >> .venv/bin/activate
echo 'export FLASK_APP=main.py' >> .venv/bin/activate

# activate the virtualenv
source .venv/bin/activate

# setup app-specific python modules
pip install -r requirements

# psql role and db creation
sudo su - postgres <<WRAP
createuser -d $USER
psql -c 'alter user $USER with createdb'
WRAP
createdb -E UTF8 -T template0 lbcalert_dev

# update db from migration files
flask db upgrade
