from flask import url_for, render_template, flash
from flask.ext.mail import Mail, Message
from bs4 import BeautifulSoup
import random
import requests
import re
import sys
import os
import json
import dateparser

from app import app, db, q
from models import Search, LBCentry

def list_items(url, proxy=None):
    if proxy is not None:
        r = requests.get(url, proxies = {"https":proxy})
    else:
        r = requests.get(url)
    
    html = r.text
    soup = BeautifulSoup(html,"html.parser")     

    section = soup.find("section",{"class":"mainList"})
    links = section.findAll("a",{"class":"list_item"})

    listings = []

    for link in links:
        listid = int(json.loads(link["data-info"])["ad_listid"])
        title = link['title'].strip()
        pricediv = link.find("h3",{"class":"item_price"})
        price = None
        if pricediv:
            m = re.match("(\d+)",pricediv.text.strip())
            price  = int(m.group(1))
        supp = [' '.join(s.text.split()) for s in link.findAll("p",{"class":"item_supp"})]
        category = supp[0]
        location = supp[1]
        time = dateparser.parse(supp[2])
        
        a = LBCentry(linkid=listid,title=title,category=category,price=price,time=time,location=location)
        listings.append(a)
        
    return listings

def parselbc(id, page):
    with app.test_request_context():
        search = Search.query.get(id)
   
        url = "/".join([app.config['LBCURL'],search.terms])

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
    list_items("https://www.leboncoin.fr/annonces/offres/ile_de_france/")