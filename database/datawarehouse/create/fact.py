from peewee import TextField, CharField, FloatField, IntegerField, Model
from database.datawarehouse.create.base import db

class FactTable(Model):

    id = CharField(null=True, primary_key=True)
    property_type = TextField(null=True)
    direction_id = CharField(null=True)
    legality_id = CharField(null=True)
    address_id = CharField(null=True)
    date_id = CharField(null=True)
    price_vnd = FloatField(null=True)
    size_sqm = FloatField(null=True)
    bedroom = IntegerField(null=True)
    bathroom = IntegerField(null=True)
    floor = IntegerField(null=True)
    source = TextField(null=True)
    description = TextField(null=True)

    class Meta:
        database = db
        table_name = "facttable"