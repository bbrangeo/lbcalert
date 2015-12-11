from flask import Flask, render_template, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import Result

@app.route('/')
def show_searches():
    # cur = g.db.execute('select id, title, terms from searches order by id desc')
    # searches = [dict(id=row[0], title=row[1], terms=row[2]) for row in cur.fetchall()]
    # print searches
    searches=[]
    return render_template('show_searches.html', searches=searches)

@app.route('/add', methods=['POST'])
def add_search():
    # g.db.execute('insert into searches (title, terms) values (?, ?)',
    #              [request.form['title'], request.form['terms']])
    # g.db.commit()
    flash('New search was successfully posted')
    return redirect(url_for('show_searches'))

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()