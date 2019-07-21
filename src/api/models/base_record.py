from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from pydantic.main import BaseModel

from db import CRUD, Database


class BaseRecordConfig(BaseModel, ABC):
    class Config:
        use_enum_values = True


class BaseRecord(BaseRecordConfig, ABC):
    """BaseRecord class to be inherited by models to work with basic DB interactions

    Keyword Arguments:
        metaclass {[type]} -- Metaclass Abstract base class to support abstract methods (default: {ABCMeta})
    """
    uuid: str = None

    @property
    @abstractmethod
    def model_name(self):
        """Returns model name to be used while creating DB tables"""
        return "base_record"

    def save(self, db: Database):
        """Persist the changed/new record to the database"""
        if self.uuid is None:
            self.uuid = CRUD.create(db, self.model_name, self.dict())
        else:
            CRUD.update(db, self.model_name, self.uuid, self.dict())

    def delete(self, db: Database):
        """Deletes the record from the database"""
        if self.uuid is None:
            raise Exception("Cannot delete: no record uuid found")
        else:
            CRUD.delete(db, self.model_name, self.uuid)
