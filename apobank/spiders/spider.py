import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ApobankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class ApobankSpider(scrapy.Spider):
	name = 'apobank'
	page = 2
	start_urls = ['https://kurse.banking.co.at/responsive/volksbank/(X(1)S(pfvdon3mlh2bgl2exg5pscp0))/Default.aspx?action=newsIntroPage&newsBranch=All&newsSegment=All&newsCategory=All&newsCountry=All&menuId=9_1&lang=de&bankID=093&AspxAutoDetectCookieSupport=1&pageRecords=1']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news_box clearfix"]/ul//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://kurse.banking.co.at/responsive/volksbank/(X(1)S(pfvdon3mlh2bgl2exg5pscp0))/Default.aspx?action=newsIntroPage&newsBranch=All&newsSegment=All&newsCategory=All&newsCountry=All&menuId=9_1&lang=de&bankID=093&AspxAutoDetectCookieSupport=1&pageRecords={self.page}'
		if self.page <= len(response.xpath('//div[@class="paging-numbers"]/a').getall()):
			self.page += 1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//span[@class="newsdat"]/text()').get().replace('\xa0', ' ').split(', ')[1]
		title = response.xpath('//div[@class="newshd"]/text()').get()
		content = response.xpath('//div[@class="grayboxnews"]//pre//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ApobankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
