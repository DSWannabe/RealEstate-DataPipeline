import json
from bds_crawling.items import Detailed_Homedy
import scrapy
from bs4 import BeautifulSoup
from datetime import datetime


class DetailedHomedy(scrapy.Spider):
    name = "homedy"

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
                "./data/raw/detailed_homedy.jsonl": {
                    "format": "jsonlines",
                    "encoding": "utf8",
                    "overwrite": True,
                }
            }
        }, priority="spider")
        return spider

    def start_requests(self):
        start_urls = []

        with open("./data/url/homedy.jsonl") as file:
            for line in file.read().splitlines():
                post = json.loads(line)
                location_url = post["url"]
                start_urls.append(f"https://homedy.com/{location_url}")

        for url in start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        product_info = []
        info_table = soup.find_all("div", class_="product-info")
        for inf in info_table:
            data = inf.get_text(strip=True, separator="|").split("|")
            product_info.append(data)
        # self.log(product_info)

        d = {}
        p_s = []
        price_size = soup.find_all("div", class_="product-short-info")
        for ps in price_size:
            data = ps.get_text(strip=True, separator="|").split("|")
            p_s.append(data)
        # self.log(p_s)

        table = []
        details = soup.find_all("div", class_="product-attributes")
        for de in details:
            items = de.find_all("div", class_="product-attributes--item")
            for it in items:
                detail = it.get_text(strip=True, separator="|").split("|")
                table.append(detail)
        # self.log(table)

        for i in range(len(table)):
            d[table[i][0]] = table[i][1]

        addr = soup.find_all("div", class_="address")
        for a in addr:
            d['address'] = a.get_text(strip=True)
        # self.log(d)

        description = soup.find_all("div", class_="description readmore", id="readmore")
        # self.log(description)

        dictionary = Detailed_Homedy(
            id=product_info[0][-1],
            source='homedy',
            time_detail=product_info[0][1],
            scraped_on=datetime.now().strftime("%d-%m-%Y"),
            price=p_s[0][1] if p_s and len(p_s[0]) > 1 else "N/A",
            price_unit=p_s[0][2] if p_s and len(p_s[0]) > 2 else "N/A",
            size=p_s[0][6] if p_s and len(p_s[0]) > 6 else "N/A",
            size_unit=p_s[0][7] if p_s and len(p_s[0]) > 7 else "N/A",
            legality=d.get("Tình trạng pháp lý") if d.get("Tình trạng pháp lý") else "N/A",
            property_type=d.get("Loại hình") if d.get("Loại hình") else "N/A",
            direction=d.get("Hướng nhà") if d.get("Hướng nhà") else "N/A",
            address=d.get("address") if d.get("address") else "N/A",
            description=description[0].get_text(strip=True) if description else "N/A",
        )
        yield dictionary
