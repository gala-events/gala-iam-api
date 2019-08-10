from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.user.user_model import (USER_MODEL_NAME, User, UserCreate,
                                    UserPartial)


class UserManager(BaseRecordManager):
    """UserManager to handle CRUD functionality"""

    model = User
    model_name = USER_MODEL_NAME

    @classmethod
    def create(cls, db: Database, record: UserCreate) -> User:
        """Creates a new User after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {UserCreate} -- New User data

        Returns:
            User -- newly created user
        """
        existing_user = UserManager.find_by_name(db, record.metadata.name)
        if existing_user:
            raise ValidationError(
                "User with name [%s] already exists" % record.metadata.name)

        return super(UserManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: UserPartial) -> User:
        """Updates the existing User after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_user = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_user.metadata.name:
            if UserManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "User with name [%s] already exists" % record.metadata.name)

        return super(UserManager, cls).update(db, record_uuid, record)
