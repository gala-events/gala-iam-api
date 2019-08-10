from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.group.group_manager import GroupManager
from models.permission.permission_model import (PERMISSION_MODEL_NAME,
                                                Permission, PermissionCreate,
                                                PermissionPartial,
                                                PermissionSubjectKind)
from models.role.role_manager import RoleManager
from models.service_account.service_account_manager import \
    ServiceAccountManager
from models.user.user_manager import UserManager


class PermissionManager(BaseRecordManager):
    """PermissionManager to handle CRUD functionality"""

    model = Permission
    model_name = PERMISSION_MODEL_NAME
    @classmethod
    def validate_permission(cls, db: Database, record: PermissionCreate):
        """Validates permission record

        Arguments:
            db {Database} -- Database connection
            record {PermissionCreate} -- New Permission data

        Raises:
            ValidationError: Raises ValidationError if subject kind is not supported
        """
        new_permission = record
        role = new_permission.role
        existing_roles = RoleManager.find(db, filter_params={
            "metadata.name": role
        })
        if not existing_roles:
            raise ValidationError(
                f"Role [{new_permission.role}] doesn't exist")

        for subject in new_permission.subjects:
            subject_kind = subject.kind
            subject_name = subject.name
            manager = None
            if subject_kind == PermissionSubjectKind.USER:
                manager = UserManager
            elif subject_kind == PermissionSubjectKind.SERVICE_ACCOUNT:
                manager = ServiceAccountManager
            else:  # subject_kind == PermissionSubjectKind.GROUP:
                manager = GroupManager

            records = manager.find(db, filter_params={
                "metadata.name": subject_name
            })
            if not records:
                raise ValidationError(
                    f"Subject [{subject_name}] of [{subject_kind}] kind doesn't exist.")

    @classmethod
    def create(cls, db: Database, record: PermissionCreate) -> Permission:
        """Creates a new Permission after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {PermissionCreate} -- New Permission data

        Returns:
            Permission -- newly created permission
        """
        existing_permission = PermissionManager.find_by_name(
            db, record.metadata.name)
        if existing_permission:
            raise ValidationError(
                "Permission with name [%s] already exists" % record.metadata.name)

        cls.validate_permission(db, record)
        return super(PermissionManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: PermissionPartial) -> Permission:
        """Updates the existing Permission after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_permission = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_permission.metadata.name:
            if PermissionManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "Permission with name [%s] already exists" % record.metadata.name)
        cls.validate_permission(db, updated_record)
        return super(PermissionManager, cls).update(db, record_uuid, record)
