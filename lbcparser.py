from flask import url_for, render_template, flash
from flask.ext.mail import Mail, Message

import random
import requests
import re
import sys
import os
import json
import dateparser
import html
import json

from flask.ext.login import login_user
from app import app, db, q, conn
from rq import Connection, get_failed_queue
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

def get_listing_url(linkid):
    url = app.config['BASE_URL'] + "view.json?" + "ad_id=" + str(linkid)
    return url + "&app_id=" + app.config['APP_ID'] + "&key=" + app.config['API_KEY']

def list_items(search, proxy=None):
    url = search.get_url()
    print("[list_items]" + str(url))

    if proxy is not None and proxy != "":
        print("[list_items] using proxy " + proxy)
        r = requests.get(url, proxies = {"https":proxy})
    else:
        r = requests.get(url)

    ads = r.json()['ads']

    listings = []

    existing_ids = [e.linkid for e in search.lbc_entries]

    for ad in ads:
        listid = int(ad['list_id'])

        if listid in existing_ids:
            continue

        listing_url = get_listing_url(listid)
        
        if proxy is not None:
            r = requests.get(listing_url, proxies = {"https":proxy})
        else:
            r = requests.get(listing_url)

        try :
            text = r.content.decode(r.encoding)
            listing_json = json.loads(text, strict=False)
        except Exception as e:
            print("[list_items] " + str(listing_url))
            print("[list items] " + str(listid) + " skipped cause : " + str(e))
            continue

        if 'body' in listing_json:
            description = listing_json['body']
        else:
            description = ""

        title = ad['subject']
        price = ad['price']
        if (price == ''):
            price = None
        else:
            price = int(price.replace(" ",""))
        category = int(ad['category_id'])

        location = ad['region_name'] + ' - ' + \
                   ad['city'] + ' (' + ad['zipcode'] + ')'
#                   ad['dpt_name'] + ' - ' + \
        time = dateparser.parse(ad['date'])
        if "thumb_hd" in ad:
            imgurl = ad['thumb_hd']
        else:
            imgurl = None
        if "list_time" in ad:
            time = ad['list_time']

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
            "description": description
        }

        #print(params)

        a = LBCentry(**params)
        print("[list_items]" + str(a))
        listings.append(a)
    return listings

def parselbc(id, page):
    with app.test_request_context():
        search = Search.query.get(id)

        listings = list_items(search, app.config['PROXY_URL'])

        new_items = []
        for listing in listings:
            if search.minprice is not None and \
                 listing.price is not None and listing.price < search.minprice:
                continue
            elif search.maxprice is not None and \
                 listing.price is not None and listing.price > search.maxprice:
                continue
            else:
                db.session.add(listing)
                search.lbc_entries.append(listing)
                new_items.append(listing)
        db.session.commit()

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
    # newproxy = requests.get("https://gimmeproxy.com/api/getProxy?curl=true&protocol=socks5&maxCheckPeriod=100&minSpeed=200").content
    # print("setting proxy " + str(newproxy))
    # app.config['PROXY_URL'] = str(newproxy)
    searches = Search.query.all()
    # Clear failed jobs
    with Connection(conn):
        fq = get_failed_queue()
    for job in fq.jobs:
            print("delete job " + job.id)
            job.delete()
    for search in searches:
        job = q.enqueue_call(
            func=parselbc, args=(search.id,1), result_ttl=0
        )

if __name__=="__main__":
    search = Search(title = "test", terms = "test", user=None)
    url = search.get_url()
    list_items(url)
