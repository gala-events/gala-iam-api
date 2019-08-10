from uuid import uuid4

from passlib.context import CryptContext
from pydantic.error_wrappers import ValidationError

from db.database import Database
from models.base_record_manager import BaseRecordManager
from models.service_account.service_account_model import (
    SERVICE_ACCOUNT_MODEL_NAME, ServiceAccount, ServiceAccountCreate,
    ServiceAccountPartial, ServiceAccountPostCreate)


class ServiceAccountManager(BaseRecordManager):
    """ServiceAccountManager to handle CRUD functionality"""

    model = ServiceAccount
    model_name = SERVICE_ACCOUNT_MODEL_NAME
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
            message = f"ServiceAccount with name [{record.metadata.name}] already exists"
            raise ValidationError(message)

        client_id = str(uuid4())
        client_secret = str(uuid4())
        new_record = ServiceAccountPostCreate(
            **record.dict(), client_id=client_id, client_secret=client_secret)

        record_to_create = new_record.copy(
            update={"client_secret": cls.pwd_context.hash(new_record.client_secret)})
        record_to_create.save(db)

        return record_to_create.dict(update={"client_secret": client_secret})

    @classmethod
    def update(cls, db: Database, record_uuid: str, record: ServiceAccountPartial) -> ServiceAccount:
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
