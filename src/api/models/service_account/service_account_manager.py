from pydantic.error_wrappers import ValidationError

from db.database import Database

from models.base_record_manager import BaseRecordManager
from models.service_account.service_account_model import SERVICE_ACCOUNT_MODEL_NAME, ServiceAccount, ServiceAccountCreate


class ServiceAccountManager(BaseRecordManager):
    """ServiceAccountManager to handle CRUD functionality"""

    model = ServiceAccount
    model_name = SERVICE_ACCOUNT_MODEL_NAME

    @classmethod
    def create(cls, db: Database, record: ServiceAccountCreate) -> ServiceAccount:
        """Creates a new ServiceAccount after validating subjects.


        Arguments:
            db {Database} -- Database connection
            record {ServiceAccountCreate} -- New ServiceAccount data

        Returns:
            ServiceAccount -- newly created service_account
        """
        existing_service_account = ServiceAccountManager.find_by_name(
            db, record.metadata.name)
        if existing_service_account:
            raise ValidationError(
                "ServiceAccount with name [%s] already exists" % record.metadata.name)

        return super(ServiceAccountManager, cls).create(db, record)

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: ServiceAccountCreate) -> ServiceAccount:
        """Updates the existing ServiceAccount after validating data

        Arguments:
            db {Database} -- Database connection
            record_uuid {str} -- unique record uuid
            record {BaseModel} -- updating record

        Returns:
            BaseRecord -- Updated record
        """
        existing_service_account = cls.find_by_uuid(db, record_uuid)
        updated_record = cls.model(**record.dict(), uuid=record_uuid)
        if updated_record.metadata.name != existing_service_account.metadata.name:
            if ServiceAccountManager.find_by_name(db, updated_record.metadata.name):
                raise ValidationError(
                    "ServiceAccount with name [%s] already exists" % record.metadata.name)

        return super(ServiceAccountManager, cls).update(db, record_uuid, record)
