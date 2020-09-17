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

u= 'https://www.channelstv.com/feed/'
response=requests.get(u)
soup=BeautifulSoup(response.content,features="xml")

#entrys=soup.findAll('entry')

#news_entrys =[]

#for item in entrys:
 #   new_item ={}
  #  new_item ['title'] = item.title.text
   # new_item ['link'] = item.link
    #new_item ['published'] = item.published.text
    #news_entrys.append(new_item)
print(soup.prettify())