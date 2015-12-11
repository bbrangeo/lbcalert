import requests
from bs4 import BeautifulSoup
import re

from app import db
from models import LBCentry

def parselbc(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html,"html.parser")
    
    lbclist = soup.find("div",{"class":"list-lbc"})
    links = lbclist.findAll("a")
    
    for link in links:
        id = int(link['href'].split('/')[4].split('.')[0])
        category = link['href'].split('/')[3]
        title = link.find("h2",{"class":"title"}).text.strip()
        a = LBCentry(id=id,title=title,category=category)
        pricediv = link.find("div",{"class":"price"})
        if pricediv:
            m = re.match("(\d+)",pricediv.text.strip())
            price  = int(m.group(1))
            a.price=price
        if LBCentry.query.filter_by(id=id).first():
            break
        else:
            db.session.add(a)
    db.session.commit()
    return