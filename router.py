from flask import render_template, request, flash, redirect, url_for

from app import app, db, q
from models import Search, LBCentry
from lbcparser import parselbc

@app.route('/')
def show_searches():
    searches = Search.query.all()
    searches = [{"s":s, "nbentries":len(s.lbc_entries), "nbnew":len([e for e in s.lbc_entries if e.new])} for s in searches]
    return render_template('show_searches.html', searches=searches)

@app.route('/add', methods=['POST'])
def add_search():
    search = Search(title=request.form['title'], terms=request.form['terms'], email=request.form['email'])
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
        func=parselbc, args=(request.args['id'],), result_ttl=0
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