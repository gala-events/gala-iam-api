from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel
from pymongo.collection import ReturnDocument

from utils import RecordNotFoundException
from .database import Database


class CRUD:

    @staticmethod
    def find(db: Database, model_name, skip: int = 0, limit: int = 25, filter_params: dict = None, sort: List[str] = None) -> List[BaseModel]:
        assert db, "DB not provided"
        assert model_name, "ModelName not provided"
        if not filter_params:
            filter_params = dict()
        if not sort:
            sort = []

        sort_params = []
        for param in sort:
            direction = 1 if param and param[0] == "-" else -1
            sort_params.append((param, direction))

        cursor = db[model_name].find(filter_params).limit(limit)
        if sort_params:
            cursor = cursor.sort(sort_params)
        data = [record for record in cursor]
        return data

    @staticmethod
    def find_by_uuid(db: Database, model_name, uuid: str) -> BaseModel:
        assert db, "DB not provided"
        assert model_name, "ModelName not provided"
        assert uuid, "%s UUID not provided" % model_name
        record = db[model_name].find_one({"uuid": uuid})
        if not record:
            raise RecordNotFoundException(model_name, uuid)
        return record

    @staticmethod
    def create(db: Database, model_name, data: dict) -> str:
        assert db, "DB not provided"
        assert model_name, "ModelName not provided"
        record_id = str(uuid4())
        data.update(uuid=record_id)
        data.update(created_at=datetime.utcnow().isoformat())
        data.update(updated_at=datetime.utcnow().isoformat())
        inserted_result = db[model_name].insert_one(data)
        if inserted_result.inserted_id is None:
            raise Exception("Failed to create %s record." % model_name)
        return record_id

    @staticmethod
    def update(db: Database, model_name, uuid: str, data: dict) -> BaseModel:
        assert db, "DB not provided"
        assert model_name, "ModelName not provided"
        assert uuid, "UUID not provided"
        data.update(uuid=uuid)
        data.update(updated_at=datetime.utcnow().isoformat())
        result = db[model_name].find_one_and_update(
            {"uuid": uuid}, {"$set": data}, return_document=ReturnDocument.AFTER)
        if result == None:
            raise RecordNotFoundException(model_name, uuid)
        return result

    @staticmethod
    def delete(db: Database, model_name, uuid: str) -> None:
        assert db, "DB not provided"
        assert model_name, "ModelName not provided"
        assert uuid, "UUID not provided"
        result = db[model_name].find_one_and_delete({"uuid": uuid})
        if result is None:
            raise RecordNotFoundException(model_name, uuid)
