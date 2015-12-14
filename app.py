from flask import Flask, render_template, flash, redirect, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import os
import requests
import re

from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

q = Queue(connection=conn)

from models import Search, LBCentry

@app.route('/')
def show_searches():
    searches = Search.query.all()
    searches = [{"id":s.id, "title":s.title, "nbentries":len(s.lbc_entries), "nbnew":len([e for e in s.lbc_entries if e.new])} for s in searches]
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
    job = q.enqueue_call(
        func=parselbc, args=(request.args['id'],), result_ttl=5000
    )
    flash('Search added to parse queue:'+job.get_id())
    return redirect(url_for('show_searches'))

@app.route("/job", methods=['GET'])
def get_job():
    job = Job.fetch(request.args['key'], connection=conn)
    if job.is_finished:
        lbcentries = Search.query.get(job.result).lbc_entries
        #TODO return of new entries
        return "Job done", 200
    else:
        return "Job not finished", 202

@app.route('/showentries')
def show_lbcentries():
    search = Search.query.get(request.args['id'])
    lbcentries = search.lbc_entries
    html = render_template('show_lbcentries.html', lbcentries=lbcentries)
    newentries = (e for e in lbcentries if e.new)
    for e in newentries:
        e.new = False
    db.session.commit()
    return html

def parselbc(id):
    search = Search.query.get(id)
    existing_ids = [e.linkid for e in search.lbc_entries]
    url = "http://www.leboncoin.fr/"+search.terms
    html = requests.get(url).text
    soup = BeautifulSoup(html,"html.parser")
    
    lbclist = soup.find("div",{"class":"list-lbc"})
    links = lbclist.findAll("a")
    
    for link in links:
        linkid = int(link['href'].split('/')[4].split('.')[0])
        #test if id already found in this search
        if linkid in existing_ids:
            break
        else:
            category = link['href'].split('/')[3]
            title = link.find("h2",{"class":"title"}).text.strip()
            a = LBCentry(linkid=linkid,title=title,category=category)
            pricediv = link.find("div",{"class":"price"})
            if pricediv:
                m = re.match("(\d+)",pricediv.text.strip())
                price  = int(m.group(1))
                a.price=price
            db.session.add(a)
            search.lbc_entries.append(a)
    db.session.commit()
    return id

if __name__ == '__main__':
    app.run()