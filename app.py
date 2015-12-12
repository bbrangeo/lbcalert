from flask import Flask, render_template, flash, redirect, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import Search, LBCentry
from parselbc import parselbc

@app.route('/')
def show_searches():
    searches = Search.query.all()
    return render_template('show_searches.html', searches=searches)

@app.route('/add', methods=['POST'])
def add_search():
    search = Search(title=request.form['title'], terms=request.form['terms'])
    db.session.add(search)
    db.session.commit()
    flash('New search was successfully posted')
    return redirect(url_for('show_searches'))

@app.route('/remove')
def remove_search():
    search = Search.query.get(request.args['id'])
    db.session.delete(search)
    db.session.commit()
    flash('Search was successfully deleted')
    return redirect(url_for('show_searches'))

@app.route('/analyse')
def analyse_lbc():
    lbcentries = parselbc(request.args['id'])
    flash('Successfully parsed link')
    return redirect(url_for('show_searches'))

@app.route('/showentries')
def show_lbcentries():
    search = Search.query.get(request.args['id'])
    lbcentries = search.lbc_entries
    return render_template('show_lbcentries.html', lbcentries=lbcentries)

if __name__ == '__main__':
    app.run()