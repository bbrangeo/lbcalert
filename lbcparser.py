from flask import url_for, render_template, flash
from flask.ext.mail import Mail, Message

import random
import requests
import re
import sys
import os
import json
import dateparser

from flask.ext.login import login_user
from app import app, db, q
from models import User, Search, LBCentry


# ps, pe, mrs, rs, ms, ccs, sqs, ros, cs, bros
# f a(all) p(private) c(company)
# c = category number
# zipcode = zipcode
# q = query
# o = page
# w ?
# ca ?
# ps - pe price range(categories)
# rs - re year range
# ms - me km range
# ccs - cce cylindre


def list_items(url, proxy=None):
    if proxy is not None:
        r = requests.get(url, proxies = {"https":proxy})
    else:
        r = requests.get(url)

    ads = r.json()['ads']

    listings = []

    for ad in ads:
        listid = int(ad['list_id'])
        title = ad['subject']
        price = ad['price']
        if (price == ''):
            price = None
        else:
            price = int(price.replace(" ",""))
        category = int(ad['category_id'])

        location = ad['region_name'] + ' - ' + \
                   ad['dpt_name'] + ' - ' + \
                   ad['city'] + ' (' + ad['zipcode'] + ')'
        time = dateparser.parse(ad['date'])
        imgurl = None
        imgnumber = None

        params={
            "linkid":listid,
            "title":title,
            "category":category,
            "price":price,
            "time":time,
            "location":location,
            "imgurl":imgurl,
            "imgnumber":imgnumber,
        }

        print(params)

        a = LBCentry(**params)
        listings.append(a)
    return listings

def parselbc(id, page):
    with app.test_request_context():
        search = Search.query.get(id)

        url = search.get_url()
        print(url)
        try:
            listings = list_items(url, app.config['PROXY_URL'])
        except:
            print(sys.exc_info())
            return id

        existing_ids = [e.linkid for e in search.lbc_entries]

        new_items = []
        for listing in listings:
            if listing.linkid in existing_ids:
                break
            else:
                db.session.add(listing)
                search.lbc_entries.append(listing)
                new_items.append(listing)
        db.session.commit()

        # r = requests.get(url_for("show_searches",_external=True))
        if len(new_items)>0:
            mail=Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[user.email for user in search.users])
            msg.html = render_template('email_entries.html', lbcentries=new_items)
            mail.send(msg)
        return id

def task():
    ping_heroku()
    refresh_searches()

def ping_heroku():
    requests.get("http://"+app.config['SERVER_NAME'])

def refresh_searches():
    searches = Search.query.all()
    for search in searches:
        job = q.enqueue_call(
            func=parselbc, args=(search.id,1), result_ttl=0
        )

if __name__=="__main__":
    search = Search(title = "test", terms = "test", user=None)
    url = search.get_url()
    list_items(url)
