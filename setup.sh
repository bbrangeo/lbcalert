# #!/bin/bash

pip install virtualenv
pip install virtualenvwrapper

echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bashrc
echo 'export PROJECT_HOME=$HOME/Devel' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc

mkvirtualenv --python=/usr/bin/python3 lbcalert
pip install -r requirements.txt

echo 'export APP_SETTINGS="config.DevelopmentConfig"'  ~/.virtualenvs/lbcalert/postactivate
echo 'export DATABASE_URL="postgresql://localhost/wordcount_dev"'  ~/.virtualenvs/lbcalert/postactivate