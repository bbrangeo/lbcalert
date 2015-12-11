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