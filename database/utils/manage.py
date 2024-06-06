# database-utils-manage.py

from typing import Any, Dict, List, TypeVar
from peewee import SqliteDatabase, ModelSelect
from database.common.models import ModelBase
from database.connection import db
from log_config import logger

T = TypeVar("T", bound=ModelBase)  # type variable bound to subclasses of ModelBase


def _store_data(dataBase: SqliteDatabase, model: T, *data) -> None:
    """
    Stores multiple records in the database for the specified model. This operation is atomic.

    :param dataBase: The database connection to use.
    :param model: The Peewee model class that defines the table where data will be inserted.
    :param data: Variable number of dictionaries containing the data to be inserted.
    :return: None
    """
    try:
        with dataBase.atomic():  # inside block is treated as a single operation - performance & data integrity
            model.insert_many(*data).execute()
    except Exception as e:
        logger.error("Failed to store data: %s", e)


def _retrieve_data(model: T, *conditions, order_by=None, limit=None):
    """
    Retrieves records from the database based on conditions, with optional ordering and limit.

    :param model: The Peewee model class to query.
    :param conditions: Conditions that filter the query results.
    :param order_by: Optional parameter to specify the order of the results.
    :param limit: Optional parameter to limit the number of results returned.
    :return: A list of model instances meeting the conditions, or None if an error occurs.
    """
    query = model.select()
    if conditions:
        query = query.where(*conditions)
    if order_by:
        query = query.order_by(*order_by)
    if limit is not None:
        query = query.limit(limit)
    try:
        return list(query)
    except Exception as e:
        logger.error("Failed to retrieve data: %s", e)
        return None


def _delete_specific(model: T, **conditions):
    """
    Deletes records from the database that meet specified conditions.

    :param model: The Peewee model class from which records will be deleted.
    :param conditions: Keyword arguments that define the conditions for deletion.
    :return: None
    """
    if not conditions:
        logger.error("Deletion request must specify at least one condition to avoid clearing all records.")
        return  # This prevents accidental deletion of all records.

    query = model.delete()
    for field_name, value in conditions.items():
        field = getattr(model, field_name, None)
        if field is None:
            logger.error(f"No such field {field_name} in the model {model.__name__}.")
            continue
        query = query.where(field == value)
    num_deleted = query.execute()
    logger.info(f'Deleted {num_deleted} records with conditions {conditions}')


def _delete_all_data(model: T):
    """
    Deletes all records from the specified model.

    :param model: The Peewee model class from which all records will be deleted.
    :return: None
    """
    query = model.delete()
    num_deleted = query.execute()  # Executes the delete query
    logger.info(f'Deleted all {num_deleted} records from History')


class ManageInterface:
    """
    Provides interface methods for interacting with the database. It supports basic CRUD operations.
    """
    @staticmethod
    def store(database: SqliteDatabase, model: T, data: List[Dict]):
        """
        Stores multiple new records in the database for the given model.

        :param database: The database connection instance.
        :param model: The database model class where records will be stored.
        :param data: A list of dictionaries representing the data to be stored.
        """
        _store_data(database, model, data)

    @staticmethod
    def retrieve(model: T, *conditions, order_by=None, limit=None):
        """
        Retrieves records from the database that meet the specified conditions.

        :param model: The database model class from which records will be retrieved.
        :param conditions: Tuple of conditions that filter the query.
        :param order_by: Optional ordering for the retrieved data.
        :param limit: Optional limit on the number of records to retrieve.
        :return: A list of model instances meeting the conditions; None if the query fails.
        """
        return _retrieve_data(model, *conditions, order_by=order_by, limit=limit)

    @staticmethod
    def delete(model: T, **conditions):
        """
        Deletes records from the database that meet the specified conditions.

        :param model: The database model class from which records will be deleted.
        :param conditions: Dictionary of conditions that filter which records to delete.
        :return: None
        """
        return _delete_specific(model, **conditions)

    @staticmethod
    def clear_all(model: T):
        """
        Deletes all records from the database for the given model.

        :param model: The database model class from which all records will be deleted.
        :return: None
        """
        return _delete_all_data(model)
