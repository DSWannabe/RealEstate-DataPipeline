# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
from scrapy.exceptions import NotConfigured
from dataclasses import asdict
from bds_crawling.items import Homedy
from bds_crawling.items import Detailed_Homedy
from bds_crawling.items import Guland
from bds_crawling.items import Detailed_Guland
from bds_crawling.items import Thuviennhadat
from bds_crawling.items import Detailed_Thuviennhadat



class BdsCrawlingPipeline:
    def __init__(self, output_folder: str, file_name: str):
        self.output_folder = output_folder
        self.file_name = file_name

    @classmethod
    def from_crawler(cls, crawler):
        output_folder = crawler.settings.get("BDS_PIPELINE_OUTPUT_FOLDER")
        if not output_folder:
            raise NotConfigured("BDS_PIPELINE_OUTPUT_FOLDER is not set")
        file_name = cls.file_name
        return cls(output_folder, file_name)

    def open_spider(self, spider):
        os.makedirs(self.output_folder, exist_ok=True)

        file_path = os.path.join(self.output_folder, self.file_name)
        self.file = open(file_path, "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, self.item_class):
            dictionary = asdict(item)
            json.dump(dictionary, self.file)
            self.file.write("\n")
        return item

class GulandURLPipeline(BdsCrawlingPipeline):
    item_class = Guland
    file_name = "guland.jsonl"
class DetailedGulandPipeline(BdsCrawlingPipeline):
    item_class = Detailed_Guland
    file_name = "detailed_guland.jsonl"
class HomedyURLPipeline(BdsCrawlingPipeline):
    item_class = Homedy
    file_name = "homedy.jsonl"
class DetailedHomedyPipeline(BdsCrawlingPipeline):
    item_class = Detailed_Homedy
    file_name = "detailed_homedy.jsonl"
class ThuviennhadatURLPipeline(BdsCrawlingPipeline):
    item_class = Thuviennhadat
    file_name = "thuviennhadat.jsonl"
class DetailedThuviennhadatPipeline(BdsCrawlingPipeline):
    item_class = Detailed_Thuviennhadat
    file_name = "detailed_thuviennhadat.jsonl"