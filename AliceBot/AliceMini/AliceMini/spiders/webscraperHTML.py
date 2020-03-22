# -*- coding: utf-8 -*-
import scrapy


class WebscraperhtmlSpider(scrapy.Spider):
    name = 'webscraperHTML'
    allowed_domains = ['amazon.com']
    start_urls = ['https://www.informationng.com/','https://punchng.com/']

    def parse(self, response):
        Title=response.css(r'.+[a-z0-9\.\-+_]+-title')
        date=response.css(r'.+[a-z0-9\.\-+_]+-date')
        if date == []:
            date=response.css('.pullright')
