from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db, q
from models import Search, LBCentry
from lbcparser import parselbc
from models import User
from Categories import categories

import re
import json

@app.route('/')
@login_required
def show_searches():
    searches = current_user.searches
    if len(searches) == 0:
        return redirect(url_for("add_search"))
    searches = [{"s":s, "nbentries":len(s.lbc_entries), "nbnew":len([e for e in s.lbc_entries if e.new])} for s in searches]
    return render_template('show_searches.html', searches=searches, categories=categories)

@app.route('/add', methods=['GET','POST'])
def add_search():
    if request.method == "POST":
        title=request.form['title']
        terms=request.form['terms']
        category=request.form['category']
        maxprice=request.form['maxprice']
        minprice=request.form['minprice']
        zipcode=re.findall("[0-9]{5}",request.form['zipcode'])
        extras = request.form['extras']
        search_id = request.form['search_id']

        if category == '':
            category = None
        else:
            category = int(category)
        if minprice == '':
            minprice = None
        else:
            minprice = int(minprice)
        if maxprice == '':
            maxprice = None
        else:
            maxprice = int(maxprice)
        if zipcode == []:
            zipcode = None
        else:
            zipcode = ','.join(zipcode)
        if extras == '':
            extras = None
        
        if search_id == "":
            print("adding new search")
            search = Search()
        else:
            print("updating search " + str(search_id))
            search = Search.query.get(int(search_id))

        search.title = title
        search.terms = terms
        search.category = category
        search.minprice = minprice
        search.maxprice = maxprice
        search.vendor = request.form['type']
        search.zipcode = zipcode
        search.extras = extras

        if search_id == "":
            db.session.add(search)
        db.session.commit()
        flash('Search was successfully posted')
        return redirect(url_for('show_searches'))
    else:
        with open("search_form.json", 'r') as file:
            search_form = json.loads(file.read())
        return render_template("add_search.html", categories=search_form["categories"])

@app.route('/edit', methods=['GET'])
def edit_search():
    search_id = request.args['id']
    search = Search.query.get(request.args['id'])
    title = search.title
    terms = search.terms
    minprice = search.minprice
    maxprice = search.maxprice
    vendor = search.vendor
    category = search.category
    zipcode = search.zipcode
    extras = search.extras
    
    with open("search_form.json", 'r') as file:
            search_form = json.loads(file.read())
    return render_template("edit_search.html",
                        categories=search_form["categories"],
                        title=title,
                        terms=terms,
                        category=category,
                        minprice=minprice,
                        maxprice=maxprice,
                        vendor=vendor,
                        zipcode=zipcode,
                        extras=extras,
                        search_id=search_id)

@app.route('/remove')
def remove_search():
    search = Search.query.get(request.args['id'])
    search.users.remove(current_user)
    if len(search.users) == 0:
        for entry in LBCentry.query.filter(LBCentry.searches.any(id=request.args['id'])).all():
            entry.searches.remove(search)
            if len(entry.searches) == 0:
                db.session.delete(entry)
        db.session.delete(search)
        flash('Search deleted')
    else:
        flash('Search unlinked from user')
    db.session.commit()
    flash('Search was successfully deleted')
    return redirect(url_for('show_searches'))

@app.route('/join')
def join_search():
    searchid = request.args['id']
    search = Search.query.get(searchid)
    if search is None:
        flash('No search with that id')
    elif current_user not in search.users:
        search.users.append(current_user)
        db.session.commit()
        flash('Joined search ' + str(searchid))
    else:
        flash('User already linked with search ' + str(searchid)) 
    return redirect(url_for('show_searches'))

@app.route('/analyse')
def analyse_lbc():
    job = q.enqueue_call(
        func=parselbc, args=(request.args['id'],1), result_ttl=0
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
@login_required
def show_lbcentries():
    search = Search.query.get(request.args['id'])
    lbcentries = search.lbc_entries
    html = render_template('show_lbcentries.html', lbcentries=lbcentries)
    newentries = (e for e in lbcentries if e.new)
    for e in newentries:
        e.new = False
    db.session.commit()
    return html

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

@app.route('/deregister' , methods=['GET'])
@login_required
def deregister():
    db.session.delete(current_user)
    db.session.commit()
    flash('User successfully deregistered')
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('show_searches'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_searches'))
