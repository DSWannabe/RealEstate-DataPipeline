import json
import scrapy
from bs4 import BeautifulSoup
from bds_crawling.items import Homedy


class HomedyApartments(scrapy.Spider):
    name = "home"

    # Customer settings
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.settings.setdict({
            "FEEDS": {
                "./data/url/homedy.jsonl": {
                    "format": "jsonlines",
                    "encoding": "utf8",
                    "overwrite": True,
                }
            }
        }, priority="spider")
        return spider

    def start_requests(self):
        start_urls = []

        for page in range(1, 100):
            start_urls.append(f"https://homedy.com/ban-can-ho-tp-ho-chi-minh/p{page}")

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

        # self.log(start_urls)
    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        apts = soup.select(".product-content")
        for apt in apts:
            url = apt.find("a", class_="title padding-hoz").get("href")
            price = apt.find("span", class_="price").get_text()
            size = apt.find("span", class_="acreage").get_text()
            address = apt.find("li", class_="address").get_text()

            dictionary = Homedy(
                url=url,
                price=price,
                size=size,
                address=address,
            )

            yield dictionary