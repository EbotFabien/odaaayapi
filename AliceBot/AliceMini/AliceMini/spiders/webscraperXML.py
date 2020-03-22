# -*- coding: utf-8 -*-
import scrapy
from ..items import AliceminiItem  
import json

class WebscraperSpider(scrapy.Spider):
    name = 'webscraper'
    #allowed_domains = ['https://punchng.com'] good
    urls=[ 'https://www.lindaikejisblog.com/', 'https://www.nairaland.com/', 'https://guardian.ng/category/news/nigeria/', 'https://www.channelstv.com/', 'https://www.premiumtimesng.com/', 'https://www.pmnewsnigeria.com/',  'https://www.independent.ng/',  'https://www.withinnigeria.com/']
    start_urls = []
    for url in urls: 
        final_url="https://api.rss2json.com/v1/api.json?rss_url=" + url +"feed"
        start_urls.append(final_url)
   
    

    def parse(self, response):
        items = AliceminiItem()
        data = json.loads(response.text)
        Title=data['feed']['title']
        for i in range(4) :
            Title_o_content=data['items'][i]['title']
            link=data['items'][i]['link']
            pubDate=data['items'][i]["pubDate"]
            Author=data['items'][i]["author"]
            content=data['items'][i]["content"]
            thumbnail=data['items'][i]["thumbnail"]
            categories=data['items'][i]['categories']
        #Title=response.css('.seg-title::text').extract().....This part of code is for me to continue with the HTML Bot
        #pubdate=response.css('.pull-right::text').extract()
            print(Author)
        #Sorry for the disorganised  code,i need to rearrange..it scrapes all the sites in the lists which are xml perfectly
