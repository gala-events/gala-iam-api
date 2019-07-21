from models.base_record_manager import BaseRecordManager
from models.permission.permission_model import Permission, PERMISSION_MODEL_NAME


class PermissionManager(BaseRecordManager):
    """PermissionManager to handle CRUD functionality"""

    model = Permission
    model_name = PERMISSION_MODEL_NAME
