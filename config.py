import os

class Config(object):
    def __getattr__(self,name):
        print("get " + name)
        return os.getenv(name)
    
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '\x08t\xd7\x06\xda\xa2$\x9f\xca\xa9\x9d\x9c\xb1\xe5\x13\x8d\xb7a\xd7L)\x9d\xf4\x8d'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LBCURL = "https://www.leboncoin.fr"
    MAIL_SERVER ="smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    #todo : hide this (and change password)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    # PROXY_URL = None
    PROXY_URL = os.getenv("PROXY_URL")
    BASE_URL = "https://mobile.leboncoin.fr/templates/api/"
    APP_ID = "leboncoin_android"
    API_KEY = "d2c84cdd525dddd7cbcc0d0a86609982c2c59e22eb01ee4202245b7b187f49f1546e5f027d48b8d130d9aa918b29e991c029f732f4f8930fc56dbea67c5118ce"


class ProductionConfig(Config):
    DEBUG = False
    SERVER_NAME = "lbcalert-pro.herokuapp.com"
    VERSION = "PROD"

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = False
    SERVER_NAME = "lbcalert-stage.herokuapp.com"
    VERSION = "STAGE"

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SERVER_NAME = "localhost:5000"
    VERSION = "DEV"

class TestingConfig(Config):
    TESTING = True
