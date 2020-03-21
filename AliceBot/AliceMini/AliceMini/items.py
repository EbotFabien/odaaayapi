# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AliceminiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Title = scrapy.Field()
    pubdate= scrapy.Field()
    Author = scrapy.Field()
    Content= scrapy.Field()
    link =  scrapy.Field()
    
    pass
