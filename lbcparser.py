import requests
import re
import json
import dateparser
import logging
import random

logger = logging.getLogger().getChild('lbcparser')
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())

from flask import render_template
from flask_mail import Mail, Message

from app import app, db
from models import User, Search, LBCentry

from proxy_manager import ProxyManager

HEADER_TEMPLATE = {
    "Content-Type" : "application/json",
    "api_key" : "ba0c2dad52b3ec",
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Accept-Language" : "fr-FR,fr;q=0.5",
    "Accept-Encoding" : "gzip, deflate, br",
    "Accept" : "*/*",
    "Referer" : "https://www.leboncoin.fr/annonces/offres/pays_de_la_loire/",
    "Origin" : "https://www.leboncoin.fr",
    "DNT" : "1",
    "Connection" : "keep-alive",
    # "Cookie": "datadome=3qvLIk4IfzkLdZAbvq-i3oUs8p9nsqll4sAn.gDG8Hfg0d~8SO5Gxm1j-819K629Iblv3aNMoKb8dOipBygUkBtVO4.V8lal6gohz7AY2T; Max-Age=31536000; Domain=.leboncoin.fr; Path=/"
}
COOKIES = {
    "datadome" : "FbFpYkJJWoFw_JTHOvO1Qx4GN0r~NytNwhULUnLvDwHqPtHvU3-aB~qAzzX05TCO2Y49PCh8eSIYcdFwTrWk1CTDxPReScw~8XcBkJjWSC",
    "Domain" : ".leboncoin.fr",
    "Path" : "/"
}

def random_user_agent():
    lines = open('user_agents').read().splitlines()
    agent =random.choice(lines)
    return agent

def fetch_listings(payload, proxy=None):
    retries = 0
    while True:
        proxymanager = ProxyManager.from_file("proxies")
        proxy = proxymanager.get_random_proxy().get_url()
        logger.info("[fetch_listings] Using proxy " + proxy)
        HEADER_TEMPLATE.update({"User-Agent":random_user_agent()})
        try:
            r = requests.post("https://api.leboncoin.fr/finder/search",
                headers = HEADER_TEMPLATE,
                cookies = COOKIES,
                json = payload,
                proxies = {"https": proxy},
                timeout = 5)
            break
        except Exception as e:
            retries+=1
            logger.warn("[fetch_listings] failed %d times, %s" % (retries,e))
            if retries == 3:
                logger.warn("[fetch_listings] abandoning")
                return {}
    try:
        logger.info("[fetch_listings] Found " + str(r.json()["total"]) + " listings")
    except:
        logger.error("[fetch_listings] couldn't get listings, LBC response below")
        logger.info(r.json())
        return {}
    return r.json()

def list_items(search):
    payload = search.get_payload()
    logger.info("[list_items]" + str(payload))

    fetch_json = fetch_listings(payload)
    try:
        if fetch_json["total"] == 0:
            return []
    except:
        logger.warn("[list_item] error with json %s", str(fetch_json))
        return []

    ads = fetch_json["ads"]
    existing_ids = [e.linkid for e in search.lbc_entries]

    listings = []
    for ad in ads:
        listid = int(ad['list_id'])
        try:
            price = int(ad['price'][0])
        except:
            logger.error("price issue with " + str(ad))
        
        # if search.minprice is not None and \
        #         price is not None and price < search.minprice:
        #     continue
        # if search.maxprice is not None and \
        #         price is not None and price > search.maxprice:
        #     continue

        # TODO check updated price and update row in DB
        if listid in existing_ids:
            continue

        description = ad["body"]

        title = ad['subject']
        category = int(ad['category_id'])

        location = ""
        if "region_name" in ad["location"]:
            location += ad['location']['region_name'] + ' - '
        if "city" in ad["location"]:
            location += ad['location']['city'] + ' - '
        if "zipcode" in ad["location"]:
            location += ad['location']['zipcode']

        time = dateparser.parse(ad['first_publication_date'])
        if ad["images"]["nb_images"] > 0:
            imgurl = ad["images"]['small_url']
        else:
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
            "description": description
        }

        #print(params)

        a = LBCentry(**params)
        logger.info("[list_items]" + str(a))
        listings.append(a)
    return listings

def parselbc(id):
    with app.test_request_context():
        search = Search.query.get(id)
        
        new_items = list_items(search)
        logger.info("[parselbc] found %d new listings" % len(new_items))

        if len(new_items)>0:
            for listing in new_items:
                #db.session.add(listing)
                search.lbc_entries.append(listing)
            db.session.commit()

            mail=Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[user.email for user in search.users])
            msg.html = render_template('email_entries.html', lbcentries=new_items)
            mail.send(msg)
        
            if search.notify == True:
                logger.info("[parselbc] notifying")
                resp = requests.post(search.notify_url, json={
                    "message": "%s - new items" % search.title,
                    "priority": 5,
                    "title": "Lbcalert"
                })
        
        return id

# For testing
if __name__=="__main__":
    import sys
    if len(sys.argv)>1:
        search = Search.query.get(sys.argv[1])
    else:
        search = Search.query.first()
    # import os    
    list_items(search)
