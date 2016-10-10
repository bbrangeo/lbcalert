from app import db
from datetime import datetime

search_entry_links = db.Table('search_entry_links',
    db.Column('search_id', db.Integer, db.ForeignKey('searches.id')),
    db.Column('lbc_entry_id', db.Integer, db.ForeignKey('lbc_entries.id'))
)

class Search(db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    terms = db.Column(db.String())
    email = db.Column(db.String())
    lbc_entries = db.relationship('LBCentry', secondary=search_entry_links, backref=db.backref('searches'))

    def __init__(self, title, terms, email):
        self.title = title
        self.terms = terms
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id)
        
class LBCentry(db.Model):
    __tablename__ = 'lbc_entries'

    id = db.Column(db.Integer, primary_key=True)
    linkid = db.Column(db.Integer)
    title = db.Column(db.String())
    category = db.Column(db.String())
    price = db.Column(db.Integer)
    new = db.Column(db.Boolean)

    def __init__(self, title, category, linkid, price=None):
        self.linkid = linkid
        self.title = title
        self.category = category
        self.new = True
        if price:
            self.price = price

    def __repr__(self):
        return '<linkid {}>'.format(self.linkid)
        
class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(10))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
 
    def __init__(self , username ,password , email):
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