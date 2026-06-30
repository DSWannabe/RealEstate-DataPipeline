from peewee import *

db = PostgresqlDatabase(
    "bds_datalake",
    user="postgres",
    password="B@dmeetsevil1999xx",
    host="172.20.238.231",
    port=5432
)

class BaseModel(Model):
    class Meta:
        database = db

class Guland(BaseModel):

    id = CharField(null=True)
    legality = CharField(null=True, max_length=100)
    floorth = CharField(null=True)
    bathroom = CharField(null=True)
    bedroom = CharField(null=True)
    width = CharField(null=True)
    length = CharField(null=True)
    direction = CharField(null=True)
    description = TextField(null=True)
    property_type = CharField()
    size = CharField(null=True)
    address = TextField(null=True)
    price = CharField(null=True)
    scraped_on = CharField(null=True)
    time_detail = TextField(null=True)
    source = TextField(null=True)

    class Meta:
        table_name = "guland"

class Homedy(BaseModel):

    id = CharField(null=True)
    size = CharField(null=True)
    size_unit = CharField(null=True)
    direction = CharField(null=True)
    description = TextField(null=True)
    property_type = CharField(null=True)
    price = CharField(null=True)
    price_unit = CharField(null=True, max_length=50)
    legality = CharField(null=True, max_length=1000)
    address = TextField(null=True)
    description = TextField(null=True)
    time_detail = TextField(null=True)
    scraped_on = TextField(null=True)
    source = TextField(null=True)

    class Meta:
        table_name = "homedy"

class Thuviennhadat(BaseModel):

    id = CharField(null=True)
    price = CharField(null=True)
    bedroom = CharField(null=True)
    bathroom = CharField(null=True)
    size = TextField(null=True)
    legality = CharField(null=True)
    furniture = CharField(null=True)
    description = TextField(null=True)
    posted_on = CharField(null=True, max_length=1000)
    project = TextField(null=True)
    address = TextField(null=True)
    property_type = TextField(null=True)
    scraped_on = TextField(null=True)
    direction = TextField(null=True)

    class Meta:
        table_name = "thuviennhadat"