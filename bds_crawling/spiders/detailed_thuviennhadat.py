import json
from bds_crawling.items import Detailed_Thuviennhadat
import scrapy
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime
from scrapy_playwright.page import PageMethod


class DetailedThuviennhadat(scrapy.Spider):
    name = "thuvien"

    @classmethod
    def update_settings(cls, settings) -> None:
        super().update_settings(settings)
        settings.set("CONCURRENT_REQUESTS", 32)
        settings.set("PLAYWRIGHT_BROWSER_TYPE", "chromium") # or "firefox" or "webkit"
        settings.set("PLAYWRIGHT_MAX_CONTEXTS", 4)
        settings.set("PLAYWRIGHT_MAX_PAGES_PER_CONTEXT", 4)
        settings.set("PLAYWRIGHT_LAUNCH_OPTIONS", {"headless": True})
        settings.set("DOWNLOAD_DELAY", 0)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.settings.setdict({
            "FEEDS": {
                "/home/anhtupham99/BDS-project/data/raw/detailed_thuviennhadat.jsonl": {
                    "format": "jsonlines",
                    "encoding": "utf8",
                    "overwrite": True,
                }
            }
        }, priority="spider")
        return spider

    def start_requests(self):
        start_urls = []

        with open("/home/anhtupham99/BDS-project/data/url/thuviennhadat.jsonl") as file:
            for line in file.read().splitlines():
                post = json.loads(line)
                url = post["url"]
                if url not in start_urls:
                    start_urls.append("https://thuviennhadat.vn" + url)

        for url in start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded"},
                    "playwright_page_methods": [
                        PageMethod("route", "**/*.{png,jpg,gif,svg,woff,woff2,ttf,css}", lambda route: route.abort()),
                        PageMethod("wait_for_selector", "#detail-section", timeout=15000),
                    ]
                },
                callback=self.parse,
            )
    def parse(self, response):
        import re
        soup = BeautifulSoup(response.text, "html.parser")

        # description
        meta = soup.find("meta", {"name": "description"})
        desc = meta['content']
        print(desc)

        # table
        def get_field(label_text):
            for block in soup.find_all("div", class_="info-estate"):
                label = block.find("div", class_="unit-name-style")
                value = block.find("div", class_="floated")
                if label and value and label_text in label.get_text():
                    return value.get_text(strip=True)
            return None
        
        # ui grid stackable segment
        def get_field_2(label_text):
            for block in soup.find_all("div", class_="four wide column"):
                label = block.find("div", class_="text-muted")
                if label and label_text in label.get_text():
                    value = block.find("div", class_="text-primary")
                    if not value:
                        # fallback: get the next sibling div
                        value = label.find_next_sibling("div")
                    return value.get_text(strip=True) if value else None
            return None
        
        # project
        project = soup.find("div", class_="thirteen wide column")
        pro_name = project.find("h1", class_="text-primary").get_text(strip=True) if project else "N/A"

        # address
        address_tag = soup.find("p", class_="text-truncate-2")
        address = address_tag.get_text(strip=True) if address_tag else "N/A"

        dictionary = Detailed_Thuviennhadat(
            description=desc,
            bedroom = get_field("Số phòng ngủ") if get_field("Số phòng ngủ") else "N/A",
            bathroom = get_field("Số phòng WC") if get_field("Số phòng WC") else "N/A",
            price = get_field("Mức giá") if get_field("Mức giá") else "N/A",
            furniture = get_field("Nội thất") if get_field("Nội thất") else "N/A",
            legality = get_field("Pháp lý") if get_field("Pháp lý") else "N/A",
            size = get_field("Diện tích") if get_field("Diện tích") else "N/A",
            posted_on = get_field_2("Ngày đăng") if get_field_2("Ngày đăng") else "N/A",
            scraped_on = datetime.now().strftime("%d-%m-%Y"),
            id = get_field_2("Mã tin") if get_field_2("Mã tin") else "N/A",
            direction = get_field("Hướng nhà") if get_field("Hướng nhà") else "N/A",
            property_type = 'Căn hộ',
            project = pro_name if pro_name else "N/A",
            address = address if address else "N/A"
        )

        yield dictionary