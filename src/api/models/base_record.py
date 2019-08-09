from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID, uuid4

from pydantic.main import BaseModel
from pydantic.schema import Schema

from db import CRUD, Database

DEFAULT_NAMESPACE = "default"


class BaseRecordConfig(BaseModel, ABC):
    class Config:
        use_enum_values = True


class BaseRecord(BaseRecordConfig, ABC):
    """BaseRecord class to be inherited by models to work with basic DB interactions

    Keyword Arguments:
        metaclass {[type]} -- Metaclass Abstract base class to support abstract methods (default: {ABCMeta})
    """
    kind: Optional[str] = Schema(..., readonly=True)
    uuid: Optional[str] = Schema(..., readonly=True)

    @property
    @abstractmethod
    def model_name(self):
        """Returns model name to be used while creating DB tables"""
        return "base_record"

    def pre_save(self, db: Database):
        """Hook to override beforing saving/updating the record"""

    def post_save(self, db: Database):
        """Hook to override after saving/updating the record"""

    def pre_delete(self, db: Database):
        """Hook to override beforing deleting the record"""

    def post_delete(self, db: Database):
        """Hook to override after deleting the record"""

    def save(self, db: Database):
        """Persist the changed/new record to the database"""
        self.kind = self.model_name

        self.pre_save(db)

        data = self.dict()
        data["metadata"] = data.get("metadata", {})
        data["metadata"]["namespace"] = data["metadata"].get(
            "namespace", DEFAULT_NAMESPACE)
        if self.uuid is None:
            self.uuid = CRUD.create(db, self.model_name, data)
        else:
            CRUD.update(db, self.model_name, self.uuid, data)

        self.post_save(db)

    def delete(self, db: Database):
        """Deletes the record from the database"""

        self.pre_delete(db)

        if self.uuid is None:
            raise Exception("Cannot delete: no record uuid found")
        else:
            CRUD.delete(db, self.model_name, self.uuid)

        self.post_delete(db)
