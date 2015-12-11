import requests
from bs4 import BeautifulSoup
import re

def parselbc(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html,"html.parser")
    
    lbclist = soup.find("div",{"class":"list-lbc"})
    links = lbclist.findAll("a")
    
    lbcentries = []
    for link in links:
        a = dict()
        a['category'] = link['href'].split('/')[3]
        a['link_num'] = int(link['href'].split('/')[4].split('.')[0])
        a['title'] = link.find("h2",{"class":"title"}).text.strip()
        price = link.find("div",{"class":"price"})
        if price:
            m = re.match("(\d+)",price.text.strip())
            a['price']  = int(m.group(1))
        lbcentries.append(a)
    
    return lbcentries