# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuCrawlItem(scrapy.Item):
    name = scrapy.Field()
    company = scrapy.Field()
    university = scrapy.Field()
    location = scrapy.Field()
    industry = scrapy.Field()
