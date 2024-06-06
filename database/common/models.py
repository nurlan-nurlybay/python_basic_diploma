# database-common-models.py

from datetime import datetime
import peewee as pw
from database.connection import db


class ModelBase(pw.Model):
    """
    Base model providing common fields and configurations for other database models.

    Attributes:
        id (AutoField): Automatically incremented primary key field.
        created_at (DateTimeField): Timestamp indicating when a record was created, set to the current time by default.
    """
    id = pw.AutoField()
    created_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        """
        Meta class with configurations for the database model.

        Attributes:
            database (SqliteDatabase): The database instance that this model will use for all database operations.
        """
        database = db  # tells which database to use for operations such as querying and saving.


class History(ModelBase):
    """
    Model to store user history including actions and responses.

    Attributes:
        user_id (IntegerField): Identifier of the user, corresponds to the Telegram user ID.
        action (TextField): Text describing the action performed by the user.
        response (TextField): Text describing the bot's response to the user's action.
    """
    user_id = pw.IntegerField()
    action = pw.TextField()
    response = pw.TextField()

    class Meta:
        """
        Meta class specifying additional configurations for the history table.

        Attributes:
            table_name (str): Specifies the name of the table used to store history records.
        """
        table_name = 'history'
