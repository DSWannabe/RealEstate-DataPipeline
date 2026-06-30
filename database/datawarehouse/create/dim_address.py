from peewee import CharField, TextField, Model
from database.datawarehouse.create.base import db

class DimAddress(Model):
    id           = CharField(primary_key=True)
    province     = CharField(null=True)
    district     = CharField(null=True)
    ward         = CharField(null=True)
    full_address = TextField(null=True)

    class Meta:
        database   = db
        table_name = "dim_address"