from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.resource.resource_model import (RESOURCE_MODEL_NAME, Resource,
                                            ResourceCreate, ResourcePartial)


class ResourceManager(BaseRecordManager):
    """ResourceManager to handle CRUD functionality"""

    model = Resource
    model_name = RESOURCE_MODEL_NAME

    @classmethod
    def create(cls, db: Database, record: ResourceCreate) -> Resource:
        """Creates a new Resource after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {ResourceCreate} -- New Resource data

        Returns:
            Resource -- newly created resource
        """
        existing_resource = ResourceManager.find_by_name(
            db, record.metadata.name)
        if existing_resource:
            raise ValidationError(
                "Resource with name [%s] already exists" % record.metadata.name)

        return super(ResourceManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: ResourcePartial) -> Resource:
        """Updates the existing Resource after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_resource = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_resource.metadata.name:
            if ResourceManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "Resource with name [%s] already exists" % record.metadata.name)

        return super(ResourceManager, cls).update(db, record_uuid, record)
