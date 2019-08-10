from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.resource.resource_manager import ResourceManager
from models.resource_action.resource_action_model import (
    RESOURCE_ACTION_MODEL_NAME, ResourceAction, ResourceActionCreate,
    ResourceActionPartial)


class ResourceActionManager(BaseRecordManager):
    """ResourceActionManager to handle CRUD functionality"""

    model = ResourceAction
    model_name = RESOURCE_ACTION_MODEL_NAME

    @classmethod
    def validate_resource_action(cls, db: Database, record: ResourceActionCreate):
        """Validates resource_action record

        Arguments:
            db {Database} -- Database connection
            record {RoleCreate} -- New Role data

        Raises:
            ValidationError: Raises ValidationError if subject kind is not supported
        """

        resource = record.metadata.resource
        resource_kind = record.metadata.resource_kind
        filter_params = {
            "metadata.resource_kind": resource_kind,
            "metadata.name": resource,
        }

        resources = ResourceManager.find(db, filter_params=filter_params)
        if not resources:
            raise ValidationError(
                f"Resource [{resource}] of type [{resource_kind}] doesn't exist")

    @classmethod
    def create(cls, db: Database, record: ResourceActionCreate) -> ResourceAction:
        """Creates a new ResourceAction after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {ResourceActionCreate} -- New ResourceAction data

        Returns:
            ResourceAction -- newly created resource_action
        """
        existing_resource_actions = ResourceActionManager.find(db, filter_params={
            "metadata.name": record.metadata.name,
            "metadata.resource_kind": record.metadata.resource_kind,
            "metadata.resource": record.metadata.resource
        })

        if existing_resource_actions:
            metadata = record.dict().get("metadata")
            raise ValidationError(
                f"ResourceAction with name [{metadata}] already exists")

        cls.validate_resource_action(db, record)
        return super(ResourceActionManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: ResourceActionPartial) -> ResourceAction:
        """Updates the existing ResourceAction after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_resource_action = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_resource_action.metadata.name:
            if ResourceActionManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "ResourceAction with name [%s] already exists" % record.metadata.name)

        cls.validate_resource_action(db, updated_record)
        return super(ResourceActionManager, cls).update(db, record_uuid, record)
