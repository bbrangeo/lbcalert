import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    LBCURL = "http://trickseek-proxyserver.appspot.com/www.leboncoin.fr/"
    MAIL_SERVER ='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'lbcbot@gmail.com'
    MAIL_PASSWORD = 's7y9QSGbKPXU'

class ProductionConfig(Config):
    DEBUG = False
    SERVER_NAME = "lbcalert-pro.herokuapp.com"

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SERVER_NAME = "lbcalert-stage.herokuapp.com"

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True