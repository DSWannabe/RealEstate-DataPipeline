from peewee import TextField, CharField, DateField, FloatField
from listings.base_listing import BaseListing

class ThuvienListing(BaseListing):
    """Guland-specific listing"""

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
