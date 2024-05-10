# database-common-models.py

from datetime import datetime
import peewee as pw
from database.connection import db


class ModelBase(pw.Model):
    created_at = pw.DateTimeField(default=datetime.now())

    class Meta:
        database = db  # tells which database to use for operations such as querying and saving.


class History(ModelBase):
    number = pw.IntegerField()
    message = pw.TextField()

    class Meta:
        table_name = 'history'
