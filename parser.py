import logging
import requests
import dateparser
import shadow_useragent
from flask import render_template
from flask_mail import Mail, Message

from app import app, db
from models import Search, LBCentry
from proxy_scheduler import lbc_proxy_manager

if __name__ == "__main__":
    logging.getLogger('lbcalert').setLevel(logging.INFO)
    logging.getLogger('lbcalert').addHandler(logging.StreamHandler())
LOGGER = logging.getLogger('lbcalert').getChild('parser')

HEADER_TEMPLATE = {
    "Content-Type":"application/json",
    "api_key":"ba0c2dad52b3ec",
    "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Accept-Language":"fr-FR,fr;q=0.5",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept":"*/*",
    "Referer":"https://www.leboncoin.fr/annonces/offres/pays_de_la_loire/",
    "Origin":"https://www.leboncoin.fr",
    "DNT":"1",
    "Connection":"keep-alive",
    "Cookie":"datadome=3qvLIk4IfzkLdZAbvq-i3oUs8p9nsqll4sAn.gDG8Hfg0d~8SO5Gxm1j-"
             "819K629Iblv3aNMoKb8dOipBygUkBtVO4.V8lal6gohz7AY2T;"
             "Max-Age=31536000; Domain=.leboncoin.fr; Path=/"
}
COOKIES = {
    "datadome":"FbFpYkJJWoFw_JTHOvO1Qx4GN0r~NytNwhULUnLvDwHqPtHvU3-"
               "aB~qAzzX05TCO2Y49PCh8eSIYcdFwTrWk1CTDxPReScw~8XcBkJjWSC",
    "Domain":".leboncoin.fr",
    "Path":"/"
}

ua = shadow_useragent.ShadowUserAgent()
def get_random_user_agent():
    agent = ua.percent(0.05)
    LOGGER.info("[shadow_useragent] using : " + agent)
    return agent

MAX_RETRIES = 5
def fetch_listings(payload):
    retries = 0
    success = None
    while success is None:
        proxy = lbc_proxy_manager.get_random_good_proxy()
        LOGGER.info("[fetch listings] Using %s", str(proxy))
        HEADER_TEMPLATE.update({"User-Agent":get_random_user_agent()})
        try:
            resp = requests.post("https://api.leboncoin.fr/finder/search",
                                 headers=HEADER_TEMPLATE,
                                 # cookies = COOKIES,
                                 json=payload,
                                 proxies={"https": proxy.get_url()},
                                 timeout=5)
            success = True
        except Exception as e:
            retries += 1
            LOGGER.warn("[fetch listings] failed %d times, %s" % (retries, e))
            lbc_proxy_manager.fail_proxy(proxy)
            if retries == MAX_RETRIES:
                success = False
    if success:
        LOGGER.info("[fetch listings] Success with %s", str(proxy))
        proxy.succeed()
        fetch_json = resp.json()
        if "url" in fetch_json.keys() and "datado" in fetch_json["url"]:
            lbc_proxy_manager.ban_proxy(proxy)
        return fetch_json
    else:
        LOGGER.warn("[fetch listings] abandoning")
        return {}

def get_entry_count(fetch_json):
    if "total" not in fetch_json:
        LOGGER.error("[get_entry_count] couldn't get listings, LBC response below")
        LOGGER.info(fetch_json)
        return 0
    else:
        entry_count = fetch_json["total"]
        LOGGER.info("[get_entry_count] Found %d listing(s)" % entry_count)
        return entry_count

def get_new_items(existing_ids, ads):
    listings = []
    for ad in ads:
        listid = int(ad['list_id'])
        if listid in existing_ids:
            continue

        try:
            price = int(ad['price'][0])
        except Exception as e:
            LOGGER.error("[get_new_items] price issue with %s - %s", str(ad), str(e))
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

        params = {
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
        LOGGER.info("[list_items]" + str(a))
        listings.append(a)
    return listings

def parselbc(_search_id):
    # database interactions within an app context
    with app.app_context():
        _search = Search.query.get(_search_id)

        payload = _search.get_payload()
        LOGGER.info("[parselbc]" + str(payload))

        fetch_json = fetch_listings(payload)
        entry_count = get_entry_count(fetch_json)

        if entry_count > 0:
            ads = fetch_json["ads"]
            existing_ids = [e.linkid for e in _search.lbc_entries]
            new_items = get_new_items(existing_ids, ads)
        else:
            new_items = []

        new_item_count = len(new_items)

        LOGGER.info("[parselbc] found %d new listings" % new_item_count)

        if new_item_count > 0:
            # commit new items to db
            for listing in new_items:
                _search.lbc_entries.append(listing)
            db.session.commit()

            LOGGER.info("[parselbc] sending email")
            mail = Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+_search.title+'"',
                          sender='lbcbot@gmail.com', recipients=[user.email for user in _search.users])
            msg.html = render_template('email_entries.html', lbcentries=new_items)
            mail.send(msg)

            # send with notification service gotify
            # url looks like "https://push.example.de/message?token=<apptoken>"
            if _search.notify:
                notify_url = _search.notify_url
                LOGGER.info("[parselbc] notifying using %s" % notify_url)
                resp = requests.post(notify_url, json={
                    "message":"%s new items" % _search.title,
                    "priority":5,
                    "title":"Lbcalert"
                }, timeout=5)
                resp.raise_for_status()
                LOGGER.info("[parselbc] notified")
        LOGGER.info("[parselbc] exiting")
        return _search_id

# For testing
if __name__ == "__main__":
    search = Search.query.first()
    search_id = search.id
    db.session.delete(search.lbc_entries[0])
    db.session.commit()
    parselbc(search_id)
