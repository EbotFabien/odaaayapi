import itertools
from multiprocessing import Process
import sys
from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from xml.etree.ElementTree import parse
import sqlite3
import requests
import urllib.error
import urllib.parse
import urllib.robotparser 
import urllib.request
import json
from time import sleep

urls= ['https://www.nairaland.com/feed','https://guardian.ng/category/news/nigeria/feed/','https://www.channelstv.com/feed/','https://www.premiumtimesng.com/feed','https://www.pmnewsnigeria.com/feed/','https://www.withinnigeria.com/feed/']
for url in urls:
    response=requests.get(url)
    soup=BeautifulSoup(response.content,features="xml")
    try:
        entrys=soup.findAll('entry')

        news_entrys =[]

        for item in entrys:
            new_item ={}
            new_item ['title'] = item.title.text
            new_item ['link'] = item.link
            new_item ['published'] = item.published.text
            new_item ['description'] = item.description
            news_entrys.append(new_item)
        print(news_entrys[0])
        print(url)
    except:
        items=soup.findAll('item')

        news_items =[]

        for item in items:
            new_item ={}
            new_item ['title'] = item.title.text
            new_item ['link'] = item.link.text
            new_item ['description'] = item.description
            new_item ['pubDate'] = item.pubDate.text
            news_items.append(new_item)
        print(news_items[0])
        print(url)


#for item in xmldoc.iterfind('feed/item'):
    #print(item.findtext('title'))
   