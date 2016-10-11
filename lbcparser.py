from flask import url_for, render_template, flash
from flask.ext.mail import Mail, Message
from bs4 import BeautifulSoup
import random
import requests
import re
import sys
import os
import json

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

    parsed_links = []

    for link in links:
        listid = int(json.loads(link["data-info"])["ad_listid"])
        title = link['title'].strip()
        pricediv = link.find("h3",{"class":"item_price"})
        price = "" 
        if pricediv:
            m = re.match("(\d+)",pricediv.text.strip())
            price  = int(m.group(1))
        supp = [' '.join(s.text.split()) for s in link.findAll("p",{"class":"item_supp"})]
        category = supp[0]
        location = supp[1]
        time = supp[2]
        
    return links

def parselbc(id, page):
    with app.test_request_context():
        search = Search.query.get(id)
   
        url = "/".join([app.config['LBCURL'],search.terms])

        try:
            links = list_items(url, app.config['PROXY_URL'])
        except:
            print(sys.exc_info())
            return id
    
        existing_ids = [e.linkid for e in search.lbc_entries]

        newitems=[]
        for link in links:
            linkid = int(link['href'].split('/')[-1].split('.')[0])
            #test if id already found in this search
            if linkid in existing_ids:
                break
            else:
                #TODO actually parse category
                category = "category"
                title = link['title'].strip()
                a = LBCentry(linkid=linkid,title=title,category=category)
                pricediv = link.find("h3",{"class":"item_price"})
                if pricediv:
                    m = re.match("(\d+)",pricediv.text.strip())
                    price  = int(m.group(1))
                    a.price=price
                db.session.add(a)
                search.lbc_entries.append(a)
                newitems.append(a)
        db.session.commit()

        # r = requests.get(url_for("show_searches",_external=True))
        if len(newitems)>0:
            mail=Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[user.email for user in search.users])
            msg.html = render_template('email_entries.html', lbcentries=newitems)
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