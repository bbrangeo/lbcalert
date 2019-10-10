import requests
import re
import json
import dateparser
import logging
import shadow_useragent

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
    "Cookie": "datadome=3qvLIk4IfzkLdZAbvq-i3oUs8p9nsqll4sAn.gDG8Hfg0d~8SO5Gxm1j-819K629Iblv3aNMoKb8dOipBygUkBtVO4.V8lal6gohz7AY2T; Max-Age=31536000; Domain=.leboncoin.fr; Path=/"
}
COOKIES = {
    "datadome" : "FbFpYkJJWoFw_JTHOvO1Qx4GN0r~NytNwhULUnLvDwHqPtHvU3-aB~qAzzX05TCO2Y49PCh8eSIYcdFwTrWk1CTDxPReScw~8XcBkJjWSC",
    "Domain" : ".leboncoin.fr",
    "Path" : "/"
}

ua = shadow_useragent.ShadowUserAgent()
def get_random_user_agent():
    agent = ua.percent(0.05)
    logger.info("[shadow_useragent] using : " + agent)
    return agent

proxymanager = ProxyManager.from_file("proxies")
def fetch_listings(payload):
    retries = 0
    while True:
        proxy = proxymanager.get_random_proxy()
        logger.info("[fetch_listings] Using proxy " + str(proxy))
        HEADER_TEMPLATE.update({"User-Agent":get_random_user_agent()})
        try:
            r = requests.post("https://api.leboncoin.fr/finder/search",
                headers = HEADER_TEMPLATE,
                # cookies = COOKIES,
                json = payload,
                proxies = {"https": proxy.get_url()},
                timeout = 5)
            break
        except Exception as e:
            logger.warn("[fetch_listings] checking proxy")
            if not proxy.test_proxy():
                proxymanager.remove_bad_proxy(proxy)
                logger.warn("[fetch_listings] deleted bad proxy, %d remaining" % len(proxymanager.proxies))
            retries+=1
            logger.warn("[fetch_listings] failed %d times, %s" % (retries,e))
            if retries == 3:
                logger.warn("[fetch_listings] abandoning")
                return {}
    return r.json()

def get_entry_count(fetch_json):
    if "total" not in fetch_json:
        logger.error("[get_entry_count] couldn't get listings, LBC response below")
        logger.info(fetch_json)
        return 0
    else:
        entry_count = fetch_json["total"]
        logger.info("[get_entry_count] Found %d listing(s)" % entry_count)
        return entry_count

def get_new_items(existing_ids, ads):
    listings = []
    for ad in ads:
        listid = int(ad['list_id'])
        if listid in existing_ids:
            continue

        try:
            price = int(ad['price'][0])
        except:
            logger.error("[get_new_items] price issue with " + str(ad))
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

        a = LBCentry(**params)
        logger.info("[list_items]" + str(a))
        listings.append(a)
    return listings

def parselbc(id):
    # database interactions within an app context
    with app.app_context():
        search = Search.query.get(id)

        payload = search.get_payload()
        logger.info("[parselbc]" + str(payload))

        fetch_json = fetch_listings(payload)
        entry_count = get_entry_count(fetch_json)

        if entry_count > 0:
            ads = fetch_json["ads"]
            existing_ids = [e.linkid for e in search.lbc_entries]
            new_items = get_new_items(existing_ids, ads)
        else:
            new_items = []

        new_item_count = len(new_items)

        logger.info("[parselbc] found %d new listings" % new_item_count)
        
        if new_item_count>0:
            # commit new items to db
            for listing in new_items:
                search.lbc_entries.append(listing)
            db.session.commit()

            logger.info("[parselbc] sending email")
            mail=Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[user.email for user in search.users])
            msg.html = render_template('email_entries.html', lbcentries=new_items)
            mail.send(msg)

            # send with notification service gotify
            # url looks like "https://push.example.de/message?token=<apptoken>"
            if search.notify == True:
                notify_url = search.notify_url
                logger.info("[parselbc] notifying using %s" % notify_url)
                resp = requests.post(notify_url, json={
                    "message": "%s new items" % search.title,
                    "priority": 5,
                    "title": "Lbcalert"
                })
                logger.info("[parselbc] notified")
        logger.info("[parselbc] exiting")
        return id

# For testing
if __name__=="__main__":    
    search_id = 94
    search = Search.query.get(search_id)
    db.session.delete(search.lbc_entries[0])
    db.session.commit()
    parselbc(search_id)