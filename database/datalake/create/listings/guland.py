from peewee import TextField, CharField, DateField, FloatField
from listings.base_listing import BaseListing

class GulandListing(BaseListing):
    """Guland-specific listing"""

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
