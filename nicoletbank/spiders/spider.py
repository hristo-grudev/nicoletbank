import scrapy

from scrapy.loader import ItemLoader

from ..items import NicoletbankItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.nicoletbank.com/blog/wp-admin/admin-ajax.php"

base_payload = "action=loadmore&query=%7B%22error%22%3A%22%22%2C%22m%22%3A%22%22%2C%22p%22%3A0%2C%22post_parent%22%3A%22%22%2C%22subpost%22%3A%22%22%2C%22subpost_id%22%3A%22%22%2C%22attachment%22%3A%22%22%2C%22attachment_id%22%3A0%2C%22name%22%3A%22%22%2C%22pagename%22%3A%22%22%2C%22page_id%22%3A0%2C%22second%22%3A%22%22%2C%22minute%22%3A%22%22%2C%22hour%22%3A%22%22%2C%22day%22%3A0%2C%22monthnum%22%3A0%2C%22year%22%3A0%2C%22w%22%3A0%2C%22category_name%22%3A%22%22%2C%22tag%22%3A%22%22%2C%22cat%22%3A%22%22%2C%22tag_id%22%3A%22%22%2C%22author%22%3A%22%22%2C%22author_name%22%3A%22%22%2C%22feed%22%3A%22%22%2C%22tb%22%3A%22%22%2C%22paged%22%3A0%2C%22meta_key%22%3A%22%22%2C%22meta_value%22%3A%22%22%2C%22preview%22%3A%22%22%2C%22s%22%3A%22%22%2C%22sentence%22%3A%22%22%2C%22title%22%3A%22%22%2C%22fields%22%3A%22%22%2C%22menu_order%22%3A%22%22%2C%22embed%22%3A%22%22%2C%22category__in%22%3A%5B%5D%2C%22category__not_in%22%3A%5B%5D%2C%22category__and%22%3A%5B%5D%2C%22post__in%22%3A%5B%5D%2C%22post__not_in%22%3A%5B%5D%2C%22post_name__in%22%3A%5B%5D%2C%22tag__in%22%3A%5B%5D%2C%22tag__not_in%22%3A%5B%5D%2C%22tag__and%22%3A%5B%5D%2C%22tag_slug__in%22%3A%5B%5D%2C%22tag_slug__and%22%3A%5B%5D%2C%22post_parent__in%22%3A%5B%5D%2C%22post_parent__not_in%22%3A%5B%5D%2C%22author__in%22%3A%5B%5D%2C%22author__not_in%22%3A%5B%5D%2C%22ignore_sticky_posts%22%3Afalse%2C%22suppress_filters%22%3Afalse%2C%22cache_results%22%3Atrue%2C%22update_post_term_cache%22%3Atrue%2C%22lazy_load_term_meta%22%3Atrue%2C%22update_post_meta_cache%22%3Atrue%2C%22post_type%22%3A%22%22%2C%22posts_per_page%22%3A9%2C%22nopaging%22%3Afalse%2C%22comments_per_page%22%3A%2250%22%2C%22no_found_rows%22%3Afalse%2C%22order%22%3A%22DESC%22%7D&page={}"
headers = {
  'authority': 'www.nicoletbank.com',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': '*/*',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.nicoletbank.com',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.nicoletbank.com/blog/',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': '__cfduid=db1c48fd12741220a1d70c2fbae1a210a1616589416; _ga=GA1.2.1367261412.1616589417; _gid=GA1.2.1913123240.1616589417; _gat_gtag_UA_25232273_1=1; smFrontpageVisits=1; _hjTLDTest=1; _hjid=7f97e090-ef12-4eca-a1fe-d31a386153f1; _hjFirstSeen=1; _hjAbsoluteSessionInProgress=1; _gat=1; __atuvc=2%7C12; __atuvs=605b3280c1094374001'
}


class NicoletbankSpider(scrapy.Spider):
	name = 'nicoletbank'
	page = 0
	start_urls = ['https://www.nicoletbank.com/blog/']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=base_payload.format(self.page))
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//div[@class="post-thumbnail"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if post_links:
			self.page += 1
			yield scrapy.Request(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		title = response.xpath('//h1[@class="entry-title"]/text()').get()
		description = response.xpath('//div[@class="entry-content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//time[contains(@class, "entry-date")]/text()').get()

		item = ItemLoader(item=NicoletbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
