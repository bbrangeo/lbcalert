import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '\x08t\xd7\x06\xda\xa2$\x9f\xca\xa9\x9d\x9c\xb1\xe5\x13\x8d\xb7a\xd7L)\x9d\xf4\x8d'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    #todo : automatically manage list
    PROXIES = ['http://bestsurfing1.appspot.com/','http://elitesurfingproxy.appspot.com/','http://getwebaddress.appspot.com/','http://browsewebfastly.appspot.com/','http://unlimit-proxy.appspot.com/','http://unblockwebsitesproxy.appspot.com','http://trickseek-proxyserver.appspot.com','http://proxy-4-web.appspot.com','https://techbum-server.appspot.com/']
    LBCURL = "www.leboncoin.fr"
    MAIL_SERVER ='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    #todo : hide this (and change password)
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
    SERVER_NAME = "unkkf54db223.naimo.koding.io:5000"

class TestingConfig(Config):
    TESTING = True