from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.group.group_model import (GROUP_MODEL_NAME, Group, GroupCreate,
                                      GroupPartial)
from models.service_account.service_account_manager import \
    ServiceAccountManager
from models.user.user_manager import UserManager


class GroupManager(BaseRecordManager):
    """GroupManager to handle CRUD functionality"""

    model = Group
    model_name = GROUP_MODEL_NAME
    @classmethod
    def validate_group(cls, db: Database, record: GroupCreate):
        """Validates group record

        Arguments:
            db {Database} -- Database connection
            record {GroupCreate} -- New Group data

        Raises:
            ValidationError: Raises ValidationError if subject kind is not supported
        """
        new_group = record
        for subject in new_group.subjects:
            subject_kind = subject.kind
            if subject_kind == "USER":
                if len(UserManager.find_by_name(db, subject.name)) is not 1:
                    raise ValidationError(
                        "User [%s] does not exist" % subject.name)

            elif subject_kind == "SERVICE_ACCOUNT":
                if len(ServiceAccountManager.find_by_name(db, subject.name)) is not 1:
                    raise ValidationError(
                        "Service Account [%s] does not exist" % subject.name)

            else:
                raise ValidationError(
                    "Subject kind %s not supported" % subject_kind)

    @classmethod
    def create(cls, db: Database, record: GroupCreate) -> Group:
        """Creates a new Group after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {GroupCreate} -- New Group data

        Returns:
            Group -- newly created group
        """
        existing_group = GroupManager.find_by_name(db, record.metadata.name)
        if existing_group:
            raise ValidationError(
                "Group with name [%s] already exists" % record.metadata.name)

        cls.validate_group(db, record)
        return super(GroupManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: GroupPartial) -> Group:
        """Updates the existing Group after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_group = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_group.metadata.name:
            if GroupManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "Group with name [%s] already exists" % record.metadata.name)
        cls.validate_group(db, updated_record)
        return super(GroupManager, cls).update(db, record_uuid, record)
