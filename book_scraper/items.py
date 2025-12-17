# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class BookItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    in_stock = scrapy.Field()
    rating = scrapy.Field()
    year = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()