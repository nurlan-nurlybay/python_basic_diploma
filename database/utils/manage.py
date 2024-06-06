# database-utils-manage.py

from typing import Any, Dict, List, TypeVar
from peewee import SqliteDatabase, ModelSelect
from database.common.models import ModelBase
import logging

T = TypeVar("T", bound=ModelBase)  # type variable bound to subclasses of ModelBase


def _store_data(db: SqliteDatabase, model: T, *data) -> None:
    try:
        with db.atomic():  # inside block is treated as a single operation - performance & data integrity
            model.insert_many(*data).execute()
    except Exception as e:
        logging.error("Failed to store data: %s", e)


def _retrieve_data(model: T, *columns: Any) -> ModelSelect:
    try:
        if columns:
            query = model.select(*columns)
        else:
            query = model.select()
        return query
    except Exception as e:
        logging.error("Failed to retrieve data: %s", e)


class ManageInterface:
    @staticmethod
    def store(db: SqliteDatabase, model: T, data: List[Dict]):
        _store_data(db, model, data)

    @staticmethod
    def retrieve(model: T, *columns: Any):
        return _retrieve_data(model, *columns)

