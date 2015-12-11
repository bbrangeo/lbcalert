from app import db

class Search(db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    terms = db.Column(db.String())

    def __init__(self, title, terms):
        self.title = title
        self.terms = terms

    def __repr__(self):
        return '<id {}>'.format(self.id)
        
class LBCentry(db.Model):
    __tablename__ = 'lbc_entries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    category = db.Column(db.String())
    link_num = db.Column(db.String())
    price = db.Column(db.Integer)

    def __init__(self, title, category, link_num, price=None):
        self.title = title
        self.category = category
        self.link_num = link_num
        if price:
            self.price = price

    def __repr__(self):
        return '<id {}>'.format(self.id)