# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanmusicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class DoubanUserItem(scrapy.Item):
    name = scrapy.Field()
    href = scrapy.Field()
    doubanid = scrapy.Field()


class DoubanUserMusicItem(scrapy.Item):
    pass


class ProxyItem(scrapy.Item):
    ip = scrapy.Field()
    port = scrapy.Field()
    type = scrapy.Field()
