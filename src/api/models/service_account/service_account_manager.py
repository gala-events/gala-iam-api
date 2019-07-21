from models.base_record_manager import BaseRecordManager
from models.service_account.service_account_model import ServiceAccount, SERVICE_ACCOUNT_MODEL_NAME


class ServiceAccountManager(BaseRecordManager):
    """ServiceAccountManager to handle CRUD functionality"""

    model = ServiceAccount
    model_name = SERVICE_ACCOUNT_MODEL_NAME
