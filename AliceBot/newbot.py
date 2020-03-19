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

lb = open('Naija.txt','r')
urls=list(lb)
finals=[]
url="https://metro.co.uk/sport/feed/"
for url in urls:
        if( url==urls[-1]):
            urllast=url
            finals.append(boylast)            
        else:
            urll = url[:-1]
            finals.append(urll)
            



def Json(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as url:
            response = url.read()
    
    try:
        data = json.loads(response)
        print('good')
        
        
    except:
        return False
   
       
def XML(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    uXML=urlopen(url)
    try:
        xmldoc = parse(uXML)#parse Xml file
        u="https://api.rss2json.com/v1/api.json?rss_url=" + url
        final_u=str(u)
        with urlopen(final_u) as url:
            response = url.read()
        data = json.loads(response)
        source=data['feed']['title']
        print(source) 
        for i in itertools.count():
            Title=data['items'][i]['title']
            link=data['items'][i]['link']
            pubDate=data['items'][i]["pubDate"]
            Author=data['items'][i]["author"]
            content=data['items'][i]["content"]
            thumbnail=data['items'][i]["thumbnail"]
            categories=data['items'][i]['categories']
            print(link)
    except:
           return False
    
#XML bot is ready ,tried testing other xml sites from  the bot file but i get a 403 response not opening.
#Currently working on the HTML bot        

if __name__=='__main__':
    #for url in finals:
    p1 = Process(target = XML(url))
    p1.start()
    p2 = Process(target = Json(url))
    p2.start()
    
    





















#def html(url):
   # data = requests.get(u)
   # soup = BeautifulSoup(data.content, 'html.parser')
   # final=str(soup)
   # if '<html>' in final : 
   #    print ('succesful')
   # else:
     #   print ('fail html')        


