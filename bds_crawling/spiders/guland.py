from bds_crawling.items import Guland
import json
import scrapy
from bs4 import BeautifulSoup

class AlonhadatApartment(scrapy.Spider):
    name = "guland"

    @classmethod
    def update_settings(cls, settings) -> None:
        super().update_settings(settings)
        settings.set("ROBOTSTXT_OBEY", False)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.settings.setdict({
            "FEEDS": {
                "./data/url/guland.jsonl": {
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
            start_urls.append(f"https://guland.vn/mua-ban-can-ho-chung-cu-tp-ho-chi-minh?page={page}")

        for url in start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True}
            )

        self.log(start_urls)
    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        apts = soup.select(".c-sdb-card__cnt")
        for apt in apts:
            url = apt.find("a").get("href")
            dictionary = Guland(
                url=url
            )
            yield dictionary

