from bds_crawling.items import Thuviennhadat
import json
import scrapy
from bs4 import BeautifulSoup

class ThuviennhadatApartment(scrapy.Spider):
    name = "thuviennhadat"

    @classmethod
    def update_settings(cls, settings) -> None:
        super().update_settings(settings)
        settings.set("ROBOTSTXT_OBEY", False)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.settings.setdict({
            "FEEDS": {
                "./data/url/thuviennhadat.jsonl": {
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
            start_urls.append(f"https://thuviennhadat.vn/ban-can-ho-chung-cu-toan-quoc?utm_source=thuviennhadat_khungtimkiem&utm_medium=internal&utm_campaign=danh_sach_tin_dang&utm_content=box_goi_y_tim_kiem.trang_chu&trang={page}")

        for url in start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"playwright": True}
            )

        self.log(start_urls)
    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        import re
        container = soup.find("aside", id="list-post-content-block")
        apts = container.find_all("div", id=re.compile(r"post-item-\d+"))
        print(apts)
        
        for apt in apts:
            url = apt.find('a').get('href')
            print(url)
            dictionary = Thuviennhadat(
                url=url
            )
            yield dictionary

