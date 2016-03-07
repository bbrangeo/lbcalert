#!/bin/bash

sudo add-apt-repository ppa:chris-lea/redis-server

sudo apt-get update
sudo apt-get install build-essential postgresql postgresql-contrib redis-server

sudo pip install --upgrade virtualenv
sudo pip install --upgrade virtualenvwrapper

echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
echo 'export PROJECT_HOME=$HOME/Devel' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc

source ~/.bashrc

mkvirtualenv -p python3 ~/.virtualenvs/lbcalert
echo 'export APP_SETTINGS="config.DevelopmentConfig"' >> ~/.virtualenvs/lbcalert/bin/postactivate
echo 'export DATABASE_URL="postgresql:///lbcalert_dev"' >>  ~/.virtualenvs/lbcalert/bin/postactivate

workon lbcalert

pip install -r requirements.txt

sudo su - postgres <<WRAP
createuser -d $USER
WRAP
createdb -E UTF8 -T template0 lbcalert_dev

python manage.py db upgrade