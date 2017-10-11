# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MastercarProductItem(scrapy.Item):
    image = scrapy.Field()
    image2 = scrapy.Field()
    MFG_PART_ID = scrapy.Field()
    description2 = scrapy.Field()
    description = scrapy.Field()
    extra = scrapy.Field()
    spec = scrapy.Field()
    pass


class MastercarPriceItem(scrapy.Item):
    MFG_PART_ID = scrapy.Field()
    price1 = scrapy.Field()
    packageQty1 = scrapy.Field()
    pass

