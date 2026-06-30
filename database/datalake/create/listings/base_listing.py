from peewee import (
    CharField, TextField, FloatField, DateField,
    ForeignKeyField
)
from database.base import BaseModel

class BaseListing(BaseModel):
    """Abstract base class for all real-estate listings"""

    post_id = CharField(primary_key=True)
    address = TextField()
    scraped_on = DateField()
    price_value = FloatField()
    price_unit = CharField()
    size_value = FloatField()
    size_unit = CharField(null=True)
    district = CharField(null=True)
    bathroom = CharField(null=True)
    bedroom = CharField(null=True)
    description = TextField(null=True)
    source = TextField(null=True)

    class Meta:
        abstract = True
