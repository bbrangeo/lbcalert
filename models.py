from app import app
from app import db
from datetime import datetime

from flask_login import current_user
from helper_functions import merge_dicts
import json

import logging

logger = logging.getLogger().getChild('models')
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

search_entry_links = db.Table('search_entry_links',
    db.Column('search_id', db.Integer, db.ForeignKey('searches.id', ondelete='CASCADE')),
    db.Column('lbc_entry_id', db.Integer, db.ForeignKey('lbc_entries.id', ondelete='CASCADE'))
)

search_user_links = db.Table('search_user_links',
    db.Column('search_id', db.Integer, db.ForeignKey('searches.id', ondelete='CASCADE')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
)

class Search(db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    terms = db.Column(db.String())
    category = db.Column(db.Integer)
    minprice = db.Column(db.Integer)
    maxprice = db.Column(db.Integer)
    lbc_entries = db.relationship('LBCentry', secondary=search_entry_links, passive_deletes=True, backref='searches')
    vendor = db.Column(db.String())
    zipcode = db.Column(db.String())
    extras = db.Column(db.String())
    notify = db.Column(db.Boolean())
    notify_url = db.Column(db.String())
    
    def __init__(
            self, 
            title = "", 
            terms = "", 
            category = None, 
            minprice = None, 
            maxprice = None, 
            user = current_user,
            vendor = "private",
            extras = None,
            zipcode = None):
        self.title = title
        self.terms = terms
        self.vendor = vendor
        if category is not None:
            self.category = category
        self.minprice = minprice
        if maxprice is not None:
            self.maxprice = maxprice
        if user is not None:
            self.users.append(user)
        if zipcode is not None:
            self.zipcode = zipcode
        if extras is not None:
            self.extras = extras

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def get_payload(self):
        payload = {
            "limit":100,
            "filters":{
                "category":{},
                "enums":{
                    "ad_type":["offer"]
                },
                "location":{},
                "keywords":{},
                "ranges":{
                    "price":{}
                }
            },
            "owner_type":"all"
        }

        payload["filters"]["keywords"]["text"] = self.terms
        if self.category is not None:
            payload["filters"]["category"]["id"] = str(self.category)
        if self.zipcode is not None:
            payload["filters"]["location"]["locations"] = [{"locationType": "city", "zipcode":zipcode} for zipcode in self.zipcode.split(",")]
        payload["owner_type"] = self.vendor
        if self.minprice is not None:
            payload["filters"]["ranges"]["price"].update({"min":self.minprice})
        if self.maxprice is not None:
            payload["filters"]["ranges"]["price"].update({"max":self.maxprice})
        if self.extras is not None:
            try:
                extra_json = json.loads(self.extras)
            except:
                extra_json = {}
                logger.warn("[get_payload] couldn't parse extras")
            payload = merge_dicts(payload,extra_json)
        return payload

class LBCentry(db.Model):
    __tablename__ = 'lbc_entries'

    id = db.Column(db.Integer, primary_key=True)
    linkid = db.Column(db.Integer)
    title = db.Column(db.String())
    category = db.Column(db.String())
    location = db.Column(db.String())
    time = db.Column(db.DateTime)
    price = db.Column(db.Integer)
    imgurl = db.Column(db.String())
    imgnumber = db.Column(db.Integer)
    new = db.Column(db.Boolean)
    description = db.Column(db.String())

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.new = True

    def __repr__(self):
        return '<linkid {}>'.format(self.linkid)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(10))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
    searches = db.relationship("Search", secondary=search_user_links, passive_deletes=True, backref='users')

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<userid {}>'.format(self.id)
