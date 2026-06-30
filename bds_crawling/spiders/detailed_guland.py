import json
from bds_crawling.items import Detailed_Guland
import scrapy
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime


class DetailedGuland(scrapy.Spider):
    name = "gu"

    @classmethod
    def update_settings(cls, settings) -> None:
        super().update_settings(settings)
        settings.set("CONCURRENT_REQUESTS", 8)
        settings.set("PLAYWRIGHT_BROWSER_TYPE", "chromium") # or "firefox" or "webkit"
        settings.set("PLAYWRIGHT_MAX_CONTEXTS", 2)
        settings.set("PLAYWRIGHT_MAX_PAGES_PER_CONTEXT", 3)
        settings.set("PLAYWRIGHT_LAUNCH_OPTIONS", {"headless": True})
        settings.set("DOWNLOAD_DELAY", 0.25)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.settings.setdict({
            "FEEDS": {
                "/home/anhtupham99/BDS-project/data/raw/detailed_guland.jsonl": {
                    "format": "jsonlines",
                    "encoding": "utf8",
                    "overwrite": True,
                }
            }
        }, priority="spider")
        return spider

    def start_requests(self):
        start_urls = []

        with open("/home/anhtupham99/BDS-project/data/url/guland.jsonl") as file:
            for line in file.read().splitlines():
                post = json.loads(line)
                url = post["url"]
                if url not in start_urls:
                    start_urls.append(url)

        for url in start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": False, # If set to True, load everything including images, css, js, ...
                },
                callback=self.parse,
            )
    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        cols = []
        details = []
        outside = []
        addresses = []
        d = {}

        #column names
        columns = soup.find_all("div", class_="s-dtl-inf__lbl")
        for col in columns:
            column = col.get_text()
            cols.append(column)

        #column values
        features = soup.find_all("div", class_="s-dtl-inf__val")
        for feature in features:
            feat = feature.get_text()
            details.append(feat)

        for i in range(len(cols)):
            d[cols[i]] = details[i]

        #values outside the table
        outside_table = soup.find_all("div", class_=["dtl-prc__sgl dtl-prc__ttl", "dtl-prc__sgl dtl-prc__dtc", "dtl-prc__sgl", ])
        for out in outside_table:
            outt = out.get_text()
            outside.append(outt)

        d["Giá"] = outside[0]
        d["kích thước"] = outside[1]
        d["trên m2"] = outside[2]
        self.log(outside)

        #address
        address = soup.find("div", class_="dtl-stl__row")
        for addr in address:
            addrr = addr.get_text()
            addresses.append(addrr)
        result = " ".join(addresses) if addresses else "N/A"

        #id
        url_id = response.url.split("/")[-1]
        id = ""
        for i in range(len(url_id)):
            if url_id[-i] != "-":
                id = url_id[-i] + id
            else:
                break

        #empty values handling
        for val in details:
            if val == "":
                details = "N/A"

        #handle dtl-stl__row
        tmp = []
        rows = soup.find_all("div", class_="dtl-stl__row")
        for row in rows:
            spans = row.find_all("span")
            tmp.append(spans)

        #description
        description = soup.find_all("div", class_="dtl-inf__dsr")
        others = ""
        for des in description:
            content = des.get_text()
            others += content

        dictionary = Detailed_Guland(
            id=id,
            source='guland',
            property_type=d.get("Loại BĐS:") if d.get("Loại BĐS:") else "N/A",
            legality=d.get("Pháp lý:") if d.get("Pháp lý:") else "N/A",
            direction=d.get("Hướng cửa chính:") if d.get("Hướng cửa chính:") else "N/A",
            floorth=d.get("Tầng số:") if d.get("Tầng số") else "N/A",
            bathroom=d.get("Số phòng tắm:") if d.get("Số phòng tắm:") else "N/A",
            bedroom=d.get("Số phòng ngủ:") if d.get("Số phòng ngủ:") else "N/A",
            width=d.get("Chiều ngang:") if d.get("Chiều ngang:") else "N/A",
            length=d.get("Chiều dài:") if d.get("Chiều dài:") else "N/A",
            price=d.get("Giá") if d.get("Giá") else "N/A",
            size=d.get("kích thước") if d.get("kích thước") else "N/A",
            address=result,
            scraped_on=datetime.now().strftime("%d-%m-%Y"),
            time_detail=tmp[1][1].get_text() if len(tmp) > 1 and len(tmp[1]) > 1 else "N/A",
            description=others
        )

        yield dictionary