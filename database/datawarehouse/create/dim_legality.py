from peewee import CharField, Model
from database.datawarehouse.create.base import db

class DimLegality(Model):
    id   = CharField(primary_key=True)
    name = CharField(null=True)

    class Meta:
        database   = db
        table_name = "dim_legality"