from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.resource.resource_manager import ResourceManager
from models.resource_action.resource_action_manager import \
    ResourceActionManager
from models.role.role_model import (ROLE_MODEL_NAME, Role, RoleCreate,
                                    RolePartial)


class RoleManager(BaseRecordManager):
    """RoleManager to handle CRUD functionality"""

    model = Role
    model_name = ROLE_MODEL_NAME
    @classmethod
    def validate_role(cls, db: Database, record: RoleCreate):
        """Validates role record

        Arguments:
            db {Database} -- Database connection
            record {RoleCreate} -- New Role data

        Raises:
            ValidationError: Raises ValidationError if subject kind is not supported
        """
        new_role = record
        for rule in new_role.rules:
            resources = ResourceManager.find(db, filter_params={
                "metadata.name": rule.resource,
                "metadata.resource_kind": rule.resource_kind,
            })
            if not resources:
                message = f"Kind [{rule.resource_kind}] doesn't exists."
                if rule.resource:
                    message = f"Resource [{rule.resource}] of {message}"
                raise ValidationError(message)

            for resource_action in rule.resource_actions:
                resource_kind = rule.resource_kind
                resource = rule.resource

                filter_params = {
                    "metadata.name": resource_action,
                    "metadata.resource_kind": resource_kind,
                    "metadata.resource": resource
                }

                actions_on_resource = ResourceActionManager.find(
                    db, filter_params=filter_params)

                if not actions_on_resource:
                    filter_params["metadata.resource"] = None
                    actions_on_resource_kind = ResourceActionManager.find(
                        db, filter_params=filter_params)
                    if not actions_on_resource_kind:
                        raise ValidationError(
                            f"ResourceAction with [{filter_params}] constraint doesn't exist.")

    @classmethod
    def create(cls, db: Database, record: RoleCreate) -> Role:
        """Creates a new Role after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {RoleCreate} -- New Role data

        Returns:
            Role -- newly created role
        """
        existing_role = RoleManager.find_by_name(db, record.metadata.name)
        if existing_role:
            raise ValidationError(
                "Role with name [%s] already exists" % record.metadata.name)

        cls.validate_role(db, record)
        return super(RoleManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: RolePartial) -> Role:
        """Updates the existing Role after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_role = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_role.metadata.name:
            if RoleManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "Role with name [%s] already exists" % record.metadata.name)
        cls.validate_role(db, updated_record)
        return super(RoleManager, cls).update(db, record_uuid, record)
