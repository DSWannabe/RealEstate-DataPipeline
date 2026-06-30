# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Homedy:
    url: str
    price: str
    size: str
    address: str

@dataclass
class Detailed_Homedy:
    id: str
    property_type: str
    direction: str
    legality: str
    time_detail: str
    scraped_on: str
    price: str
    size: str
    price_unit: str
    size_unit: str
    address: str
    description: str
    source: str

@dataclass
class Detailed_Guland:
    id: str
    property_type: str
    legality: str
    direction: str
    floorth: str
    bathroom: str
    bedroom: str
    width: str
    length: str
    price: str
    address: str
    scraped_on: datetime
    time_detail: str
    description: str
    size: str
    source: str

@dataclass
class Guland:
    url: str

@dataclass
class Thuviennhadat:
    url: str

@dataclass
class Detailed_Thuviennhadat:
    id: str
    price: str
    bedroom: str
    bathroom: str
    size: str
    legality: str
    furniture: str
    description: str
    posted_on: str
    project: str
    address: str
    property_type: str
    scraped_on: str
    direction: str