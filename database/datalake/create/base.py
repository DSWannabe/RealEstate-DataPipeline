from peewee import Model
from database.db import db

class BaseModel(Model):
    """Common ORM configuration for all models"""
    class Meta:
        database = db
        legacy_table_names = False
