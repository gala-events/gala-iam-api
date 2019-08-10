import re
from re import IGNORECASE
from typing import List, Union

from pydantic.error_wrappers import ValidationError
from pydantic.main import BaseModel

from db import CRUD, Database
from models.base_record import DEFAULT_NAMESPACE, BaseRecord
from utils.exceptions import RecordNotFoundException
from utils.json_merge_patch import json_merge_patch


class BaseRecordManager:

    model: [BaseRecord] = BaseModel
    model_name: str = "base_record"

    @classmethod
    def create(cls, db: Database, record: BaseModel) -> BaseRecord:
        """Creates an record entry in the Database

        Arguments:
            db {Database} -- Database connection
            record {BaseModel} -- BaseModel subclass describing actual model implementation

        Returns:
            BaseRecord -- BaseRecord subclass instance which has been persisted in DB
        """
        new_record = cls.model(**record.dict())
        new_record.save(db)
        return new_record

    @classmethod
    def find(cls, db: Database, skip: int = 0, limit: int = 25, sort: List[str] = None, search: str = None, search_fields: List[str] = None, filter_params=None) -> List[BaseRecord]:
        """Fetches Records from Database with filtering and searching support

        Arguments:
            db {Database} -- Database connection

        Keyword Arguments:
            skip {int} -- Number of records to be skipped based on index (default: {0})
            limit {int} -- Number of records to be returned (default: {25})
            sort {List[str]} -- Sort order, based on records property name. This supports nested keys as well (default: {None})
            search {str} -- Search records based on search_fields (default: {None})
            search_fields {List[str]} -- Provides override for the search feature, basic support is added on uuid and name. This supports nested keys as well (default: {None})

        Returns:
            List[BaseRecord] -- List of BaseRecord instances that are persisted in DB
        """
        if filter_params is None or not isinstance(filter_params, dict):
            filter_params = dict()

        if search_fields is None:
            search_fields = ["uuid"]

        if search:
            filter_params["$or"] = []
            for search_field in search_fields:
                filter_params["$or"].append({
                    search_field: re.compile(search, re.IGNORECASE)
                })

        data = CRUD.find(db, cls.model_name, skip=skip,
                         limit=limit,
                         filter_params=filter_params,
                         sort=sort)
        return [cls.model(**d) for d in data]

    @classmethod
    def find_by_uuid(cls, db: Database, record_uuid: str) -> BaseRecord:
        """Fetches a single unique record based on records uuid.

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- Record unique uuid

        Returns:
            BaseRecord -- BaseRecord subclass instance which has been persisted in DB
        """
        data = CRUD.find_by_uuid(
            db, cls.model_name, record_uuid)
        record = cls.model(**data)
        return record

    @classmethod
    def find_by_name(cls, db: Database, name: str, unique=True) -> Union[BaseRecord, List[BaseRecord]]:
        """Finds record/records based on name.

        Arguments:
            db {Database} -- Database connection
            name {str} -- name of the record

        Keyword Arguments:
            unique {bool} -- Toggles the methods behaviour to raise if multiple records found (default: {True})

        Raises:
            ValidationError: Raise ValidationError if no records are fetched
            ValidationError: Raise ValidationError if unique is passed as True and multiple records are fetched

        Returns:
            List[BaseRecord] -- Returns a list of BaseRecord.
        """
        records = cls.find(db, search=name, search_fields=[
            "name", "metadata.name"])

        if unique:
            if len(records) > 1:
                errors = ["Multiple %ss found with name [%s]" %
                          (cls.model.__name__, name)]
                raise ValidationError(errors)

        return records

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: BaseModel) -> BaseRecord:
        """Updates the record as it is passed

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        updated_record.save(db)
        return updated_record

    @classmethod
    def partial_update(cls, db: Database, record_uuid: str, record: BaseModel) -> BaseRecord:
        """Update existing record by partial changes

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record data

        Returns:
            BaseRecord -- Updated record
        """
        existing_record = cls.find_by_uuid(db, record_uuid)
        updated_record_data = json_merge_patch(
            existing_record.dict(), record.dict(skip_defaults=True))
        updated_record_data.update(uuid=record_uuid)
        updated_record = cls.model(**updated_record_data)
        updated_record.save(db)
        return updated_record

    @classmethod
    def delete(cls, db, record_uuid: str) -> BaseRecord:
        """Deletes existing record

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid

        Returns:
            BaseRecord -- Deleted record
        """
        record: BaseRecord = cls.find_by_uuid(db, record_uuid)
        record.delete(db)
        return record
