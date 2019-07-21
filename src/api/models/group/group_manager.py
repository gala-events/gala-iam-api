from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.group.group_model import GROUP_MODEL_NAME, Group, GroupCreate
from models.service_account.service_account_manager import \
    ServiceAccountManager
from models.user.user_manager import UserManager


class GroupManager(BaseRecordManager):
    """GroupManager to handle CRUD functionality"""

    model = Group
    model_name = GROUP_MODEL_NAME

    @classmethod
    def create(cls, db: Database, record: GroupCreate) -> Group:
        """Creates a new Group after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {GroupCreate} -- New Group data

        Raises:
            ValidationError: Raises ValidationError if subject kind is not supported

        Returns:
            Group -- newly created group
        """
        new_group = record
        for subject in new_group.subjects:
            subject_kind = subject.kind
            if subject_kind == "USER":
                UserManager.find_by_name(db, subject.name)

            elif subject_kind == "SERVICE_ACCOUNT":
                ServiceAccountManager.find_by_name(db, subject.name)

            else:
                raise ValidationError(
                    "Subject kind %s not supported" % subject_kind)

        return super(GroupManager, cls).create(db, record)
