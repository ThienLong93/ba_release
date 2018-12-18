# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class URLText(scrapy.Item):
    url     = scrapy.Field(serialize=str)
    text    = scrapy.Field(serialize=str)