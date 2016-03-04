#!/bin/bash

sudo pip install --upgrade virtualenv
sudo pip install --upgrade virtualenvwrapper

echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
echo 'export PROJECT_HOME=$HOME/Devel' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc

source ~/.bashrc

mkvirtualenv -p python3 ~/.virtualenvs/lbcalert
echo 'export APP_SETTINGS="config.DevelopmentConfig"' >> ~/.virtualenvs/lbcalert/bin/postactivate
echo 'export DATABASE_URL="postgresql://localhost/lbcalert_dev"' >>  ~/.virtualenvs/lbcalert/bin/postactivate

workon lbcalert

pip install -r requirements.txt