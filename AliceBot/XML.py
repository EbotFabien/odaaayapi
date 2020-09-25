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
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

urls= ['https://www.channelstv.com/feed/']
for url in urls:
    response=requests.get(url,verify = False)
    soup=BeautifulSoup(response.content,features="xml")
    headers = {'API-KEY': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiQm9vZ2llIiwidXVpZCI6ImE2MDA4YWRkLWNmMmEtNDE4NS1iNmE4LWNlMjE2YzY1MzI5OCIsImlhdCI6MTU5NjA5ODA4M30.pKwSjDoC3AboeVW3Xe8yY8hIfuKhqT86IRbP13Y7ovE','Content-type': 'application/json', 'Accept': 'text/plain'}
    
    if soup.findAll('entry') is not None:
        entrys=soup.findAll('entry')

        news_entrys =[]

        for item in entrys:
            new_item ={}
            new_item ['title'] = item.title.text
            new_item ['link'] = item.link.get('href')
            news_entrys.append(new_item)
        for i in news_entrys:
            response=requests.get(i['link'])
            soup=BeautifulSoup(response.content,'lxml')
            metas=soup.findAll('meta')

            for j in metas:
                if j.get('property') == "og:image":
                    i['thumbnail']=j.get('content')

        for i in news_entrys:
            Title= i['title']
            Link=i['link']
            sum_content=''
            LANGUAGE= "english"
            SENTENCES_COUNT = 10
            parser = HtmlParser.from_url(Link, Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)
            for sentence in summarizer(parser.document, SENTENCES_COUNT):
                    sum_content += '\n'+str(sentence)
            
            if 'thumbnail' in i:
                Thumbnail=i['thumbnail']
                params = { 
                    "title": Title,
                    "channel":["Webb-Martin","Chapman LLC","Jensen, Hudson and Peterson"],
                    "type":4,
                    "post_url": Link,
                    "thumb":Thumbnail,
                    "content":sum_content,
                    "lang":"en",

                }
                requests.post(url="https://d5db74a60e4b.ngrok.io/api/v1/post",data=json.dumps(params),headers=headers,verify=False)
                
                
            else:
                params = { 
                    "title": Title,
                    "channel":["Webb-Martin","Chapman LLC","Jensen, Hudson and Peterson"],
                    "type":4,
                    "post_url": Link,
                    "content":sum_content,
                    "lang":"en",

                }
                requests.post(url="https://d5db74a60e4b.ngrok.io/api/v1/post",data=json.dumps(params),headers=headers,verify=False)
                
    if soup.findAll('item') is not None:
        items=soup.findAll('item')
        news_items =[]

        for item in items:
            new_item ={}
            new_item ['title'] = item.title.text
            new_item ['link'] = item.link.text
            news_items.append(new_item)
        for i in news_items:
            response=requests.get(i['link'])
            soup=BeautifulSoup(response.content,'lxml')
            metas=soup.findAll('meta')

            for j in metas:
                if j.get('property') == "og:image":
                    i['thumbnail']=j.get('content')
        for i in news_items:
            Title= i['title']
            Link=i['link']
            sum_content=''
            LANGUAGE= "english"
            SENTENCES_COUNT = 10
            parser = HtmlParser.from_url(Link, Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)
            for sentence in summarizer(parser.document, SENTENCES_COUNT):
                    sum_content += '\n'+str(sentence)
            if 'thumbnail' in i:
                Thumbnail=i['thumbnail']
                params = { 
                   "title": Title,
                    "channel":["Webb-Martin","Chapman LLC","Jensen, Hudson and Peterson"],
                    "type":4,
                    "post_url": Link,
                    "thumb":Thumbnail,
                    "content":sum_content,
                    "lang":"en",
                }
                requests.post(url="https://d5db74a60e4b.ngrok.io/api/v1/post",data=json.dumps(params),headers=headers,verify=False)
                
            else:
                params = { 
                    "title": Title,
                    "channel":["Webb-Martin","Chapman LLC","Jensen, Hudson and Peterson"],
                    "type":4,
                    "post_url": Link,
                    "content":sum_content,
                    "lang":"en",
                   
                }
                
                requests.post(url="https://d5db74a60e4b.ngrok.io/api/v1/post",data=json.dumps(params),headers=headers,verify=False)
                
#for item in xmldoc.iterfind('feed/item'):
    #print(item.findtext('title'))
   #'https://www.nairaland.com/feed','https://guardian.ng/category/news/nigeria/feed/','https://www.channelstv.com/feed/'
   #'https://www.premiumtimesng.com/feed/','https://www.pmnewsnigeria.com/feed','https://www.withinnigeria.com/feed/','https://www.nairaland.com/feed','https://guardian.ng/category/news/nigeria/feed/',