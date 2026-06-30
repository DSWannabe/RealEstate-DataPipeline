from peewee import TextField, CharField, DateField, FloatField
from listings.base_listing import BaseListing

class ThuvienListing(BaseListing):
    """Guland-specific listing"""

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
        table_name = "guland"
