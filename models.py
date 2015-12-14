from app import db

entries = db.Table('entries',
    db.Column('search_id', db.Integer, db.ForeignKey('searches.id')),
    db.Column('lbc_entry_id', db.Integer, db.ForeignKey('lbc_entries.id'))
)

class Search(db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    terms = db.Column(db.String())
    lbc_entries = db.relationship('LBCentry', secondary=entries, backref='searches')

    def __init__(self, title, terms):
        self.title = title
        self.terms = terms

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
        return '<id {}>'.format(self.id)