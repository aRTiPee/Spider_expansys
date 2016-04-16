# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ExpansysItem(Item):

	url = Field()
	title = Field()
	current_price = Field()
	currency = Field()
	categories = Field()
	price = Field()
	crawl_time = Field()
	primary_image_url = Field()
	retailer_sku_code = Field()