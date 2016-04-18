from scrapy.spiders import Spider, Request

from expansys.items import ExpansysItem
import time

class ExpansysSpider (Spider):
	name = "expansys"
	allowed_domains = ["expansys.com.sg"]
	start_urls = [
		"http://www.expansys.com.sg",
	]
	def parse(self, response):
		urls = response.xpath('//div[@id="nav"]/ul/li/a/@href').re(r"http://www.expansys.com.sg/[\w\W]+")
		urls.remove(urls[-1])
		count = 1
		for x in urls:
			if count == 6:
				yield Request(x, callback=self.parse_gadgetsNav)
				count+=1
				continue
			elif count == 3:
				count+=1
				continue
			yield Request(x, callback=self.parse_mainCategory)
			count += 1

	def parse_mainCategory(self, response):
		urls = response.xpath('//div[@class="productGrid"]/ul/li[@class="title"]/h3/a/@href').extract()
		for x in urls:
			url = response.urljoin(x)
			yield Request(url, callback=self.parse_contents)


		urls = response.xpath('//li[@class="next"]/a[@class="next"]/@href').extract()
		for x in urls:
			url = response.urljoin(x)
			yield Request(url, callback=self.parse_mainCategory)

		urls = response.xpath('//ul[@class="show"]/li/ul/li/a[contains(text(), "Accessories")]/@href').extract()
		for x in urls:
			url = response.urljoin(x)
			yield Request(url, callback=self.parse_accessories)

	def parse_accessories(self, response):
		urls = response.xpath('//li/h3/a/@href').extract()
		for x in urls:
			url = response.urljoin(x)
			yield Request(url, callback=self.parse_contents)

		urls = response.xpath('//li/ul/li/a[contains(text(), "Next")]/@href').extract()
		url = response.urljoin(urls[0])
		yield Request(url, callback=self.parse_accessories)

	def parse_gadgetsNav(self, response):
		count = 1
		urls = response.xpath('//div/div/div/div/ul[@class="onpagenav"]/li/a/@href').extract()
		for x in urls:
			if not count == 1:
				url = response.urljoin(x)
				yield Request(url, callback=self.parse_gadgets)
			count += 1

	def parse_gadgets(self, response):
		urls = response.xpath('//div[@class="product_list"]/ul/li/h3/a/@href').extract()
		for x in urls:
			url = response.urljoin(x)


	def parse_contents(self, response):
		item = ExpansysItem()
		item['url'] = response.xpath('/html/head/link[1]/@href').extract()
		item["title"] = response.xpath('//div[@id="title"]/h1[@itemprop="name"]/text()').extract()
		current_price1 = response.xpath('//span[@itemprop="price"]/text()').extract()
		current_price2 = response.xpath('//span[@itemprop="price"]/sup/text()').extract()
		current_price3 = []
		if current_price1 and current_price2:
			current_price3.append(current_price1[0][3:] + current_price2[0])
			xs = current_price3.pop(0)
			count = 0
			for x in xs:
				if x == ",":
					current_price4 = xs[:count] + xs[count+1:]
					current_price3.append(current_price4)
					break
				elif count >= len(xs)-1:
					current_price3.append(xs)
				count += 1
			item['current_price'] = current_price3
		if current_price3:
			item['currency'] = response.xpath('//span[@itemprop="price"]/text()').re(r'\w+[$]')
		item['categories'] = response.xpath('//ul[@id="breadcrumbs"]/li[contains(@class, "level")]/a/span/text()').extract()
		price1 = response.xpath('//strike[@class="was"]/text()').extract()
		price2 = response.xpath('//strike[@class="was"]/sup/text()').extract()
		price3 = []
		if price1 and price2:
			price3.append(price1[0][3:] + price2[0])
			xs = price3.pop(0)
			count = 0
			for x in xs:
				if x == ",":
					price4 = xs[:count] + xs[count+1:]
					price3.append(price4)
					break
				elif count >= len(xs)-1:
					price3.append(xs)
				count += 1
			item['price'] = price3
		else:
			if current_price3:
				item['price'] = current_price3
		crawlTime = []
		crawlTime.append(time.strftime('%Y-%m-%d') + " " + time.strftime('%H:%M:%S'))
		item['crawl_time'] = crawlTime
		print time.strftime('%H:%M:%S')
		item['primary_image_url'] = response.xpath('//div[@id="image"]/a/@href').extract()
		item['retailer_sku_code'] = response.xpath('//ul[@class="product-sku"]/li/span[contains(@content, "sku")]/text()').extract()
		yield item