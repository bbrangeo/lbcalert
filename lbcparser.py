import requests
import re
import sys
import os
import json
import dateparser
import logging
import copy

from flask import url_for, render_template, flash
from flask_mail import Mail, Message

from app import app, db
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

HEADERS = {
    "Content-Type" : "application/json",
    "api_key" : "ba0c2dad52b3ec"
}
PAYLOAD = {
    "limit":100,
    "filters":{
        "category":{},
        "enums":{
            "ad_type":["offer"]
        },
        "location":{},
        "keywords":{},
        "ranges":{
            "price":{}
        }
    },
    "owner_type":"all"
}

# obtained from https://stackoverflow.com/a/7205107/34871
def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def get_listing_url(linkid):
    url = app.config['BASE_URL'] + "view.json?" + "ad_id=" + str(linkid)
    return url + "&app_id=" + app.config['APP_ID'] + "&key=" + app.config['API_KEY']

def get_search_payload(search):
    payload = copy.deepcopy(PAYLOAD)
    payload["filters"]["keywords"]["text"] = search.terms
    if search.category is not None:
        payload["filters"]["category"]["id"] = str(search.category)
    if search.zipcode is not None:
        payload["filters"]["location"]["city_zipcodes"] = [{"zipcode":zipcode} for zipcode in search.zipcode.split(",")]
    payload["owner_type"] = search.vendor
    if search.minprice is not None:
        payload["filters"]["ranges"]["price"].update({"min":search.minprice})
    if search.maxprice is not None:
        payload["filters"]["ranges"]["price"].update({"max":search.maxprice})
    if search.extras is not None:
        try:
            extra_json = json.loads(search.extras)
            payload = merge(payload,extra_json)
        except:
            pass
    return payload

def fetch_listings(payload):
    r = requests.post("https://api.leboncoin.fr/finder/search",
        headers = HEADERS,
        json = payload)
    return r.json()

    # if proxy is not None and proxy != "":
    #     logger.info("[list_items] using proxy " + proxy)
    #     r = requests.get(url, proxies = {"https":proxy})
    # else:
    #     r = requests.get(url)

def list_items(search, proxy=None):
    logger = logging.getLogger('rq.worker')

    payload = get_search_payload(search)
    logger.info("[list_items]" + str(payload))

    ads = fetch_listings(payload)["ads"]

    listings = []

    existing_ids = [e.linkid for e in search.lbc_entries]

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
            # existing_entry = LBCentry.query.get(listid)
            # if price >= existing_entry.price:
            #     continue

        # listing_url = get_listing_url(listid)
        
        # if proxy is not None:
        #     r = requests.get(listing_url, proxies = {"https":proxy})
        # else:
        #     r = requests.get(listing_url)
        # try :
        #     text = r.content.decode(r.encoding)
        #     listing_json = json.loads(text, strict=False)
        # except Exception as e:
        #     logger.error("[list_items] " + str(listing_url))
        #     logger.error("[list items] " + str(listid) + " skipped cause : " + str(e))
        #     continue
        # if 'body' in listing_json:
        #     description = listing_json['body']
        # else:
        #     description = ""

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

def parselbc(id, page):
    with app.test_request_context():
        search = Search.query.get(id)

        new_items = list_items(search, app.config['PROXY_URL'])

        if len(new_items)>0:
            for listing in new_items:
                db.session.add(listing)
                search.lbc_entries.append(listing)
            db.session.commit()

            mail=Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[user.email for user in search.users])
            msg.html = render_template('email_entries.html', lbcentries=new_items)
            mail.send(msg)
        return id


# For testing
if __name__=="__main__":
    search = Search(title = "test", terms = "test", user=None)
    url = search.get_url()
    list_items(url)
