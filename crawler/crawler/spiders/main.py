import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from crawler.items import URLText
import os

class ScrapingSpider(scrapy.Spider):    
    name = 'scrapy_results'                

    def __init__(self, *args, **kwargs):
        # get parameters from django request
        self.url                = kwargs.get('url')
        self.domain             = kwargs.get('domain')
        self.selector           = kwargs.get('selector')
        self.pid                = kwargs.get('pid')
        self.start_urls         = [self.url]
        self.allowed_domains    = [self.domain]        

    # create object to extract links from web pages
    rules = (Rule(LxmlLinkExtractor(allow=()), callback='parse', follow=True),)    

    def parse(self, response):    
        # create a URLText item object and fill the attributes            
        il = ItemLoader( item=URLText(), response=response )
        il.add_value( 'url', response.url )
        il.add_css( 'text', self.selector )        

        # iterate over every link and perform the same parse operation
        # depth-first
        for link in LxmlLinkExtractor(allow=self.allowed_domains,deny = ()).extract_links(response):                    
            yield response.follow( link.url, callback=self.parse )                  

        yield il.load_item()